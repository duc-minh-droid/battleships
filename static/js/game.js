/* Battle page: fire at the enemy grid, animate both turns from the /attack response. */
(function () {
  const BS = window.BS;
  const { sleep, label, pretty } = BS;
  const N = GAME.board.length;
  const DIFF = { easy: 'Cadet AI', hard: 'Captain AI', expert: 'Admiral AI' };

  const enemy = BS.buildBoard(document.getElementById('enemyBoard'), N, fire);
  const own = BS.buildBoard(document.getElementById('ownBoard'), N);
  const ownWrap = document.getElementById('ownWrap');
  document.getElementById('diffChip').textContent = DIFF[GAME.difficulty] || GAME.difficulty;

  const fleetOrder = Object.entries(GAME.ships).sort((a, b) => b[1] - a[1]);
  const stats = { shots: 0, hits: 0 };
  let busy = false;
  let over = false;

  /* ---------- own fleet from the board the server rendered ---------- */
  const ownShips = {};
  GAME.board.forEach((row, y) => row.forEach((cell, x) => {
    if (cell) (ownShips[cell] = ownShips[cell] || []).push([x, y]);
  }));
  const ownHp = {};
  Object.entries(ownShips).forEach(([name, cells]) => {
    const v = cells.length > 1 && cells[0][0] === cells[1][0];
    const x = Math.min(...cells.map((c) => c[0]));
    const y = Math.min(...cells.map((c) => c[1]));
    own.ships.appendChild(BS.makeShip(name, cells.length, x, y, v));
    ownHp[name] = cells.length;
  });

  function fleetList(el, prefix) {
    el.innerHTML = fleetOrder.map(([name, len]) =>
      `<li id="${prefix}-${name}"><span>${pretty(name)}</span><span class="hp">${'<i></i>'.repeat(len)}</span></li>`).join('');
  }
  fleetList(document.getElementById('enemyFleet'), 'ef');
  fleetList(document.getElementById('ownFleet'), 'of');

  function flashRow(id) {
    const li = document.getElementById(id);
    li.classList.remove('flash'); void li.offsetWidth; li.classList.add('flash');
    return li;
  }

  /* ---------- HUD ---------- */
  function setTurn(who) {
    const t = document.getElementById('turn');
    t.className = 'turn' + (who === 'enemy' ? ' enemy' : who === 'over' ? ' over' : '');
    document.getElementById('turnText').textContent =
      who === 'enemy' ? 'Enemy is targeting...' : who === 'over' ? 'Battle over' : 'Your turn - pick a target';
    enemy.root.classList.toggle('targetable', who === 'you');
    enemy.root.classList.toggle('locked', who !== 'you');
    ownWrap.classList.toggle('scanning', who === 'enemy');
  }
  function updateStats() {
    const acc = stats.shots ? Math.round((100 * stats.hits) / stats.shots) + '%' : '-';
    document.getElementById('sShots').textContent = stats.shots;
    document.getElementById('sHits').textContent = stats.hits;
    document.getElementById('sAcc').textContent = acc;
    return acc;
  }
  function log(who, text, kind) {
    const li = document.createElement('li');
    li.className = kind;
    li.innerHTML = `<i></i><span class="who">${who}</span><span>${text}</span>`;
    document.getElementById('log').prepend(li);
  }

  /* ---------- animation pieces ---------- */
  async function impact(board, x, y, hit, isEnemyShot) {
    await BS.incoming(board.fx, x, y, isEnemyShot);
    if (hit) BS.explode(board.fx, x, y, board);
    else BS.splash(board.fx, x, y);
    BS.mark(board.marks, x, y, hit ? 'hit' : 'miss');
    board.cell(x, y).classList.add('shot');
  }

  async function sinkEnemy(sunk, ghost) {
    const cells = sunk.cells;
    const v = cells.length > 1 && cells[0][0] === cells[1][0];
    const x = Math.min(...cells.map((c) => c[0]));
    const y = Math.min(...cells.map((c) => c[1]));
    const ship = BS.makeShip(sunk.name, cells.length, x, y, v, ghost ? 'enemy ghost' : 'enemy');
    enemy.ships.appendChild(ship);
    if (ghost) return;
    await sleep(60);
    ship.classList.add('sinking');
    BS.bubbles(enemy.fx, cells);
    cells.forEach(([cx, cy]) => {
      const m = enemy.marks.querySelector(`[data-key="${cx},${cy}"]`);
      if (m) m.classList.add('dead');
    });
    BS.toast(enemy.sea, 'Enemy ' + pretty(sunk.name) + ' sunk!');
    flashRow('ef-' + sunk.name).classList.add('sunk');
    log('YOU', 'sank the enemy ' + pretty(sunk.name), 'sunk');
    await sleep(950);
  }

  async function sinkOwn(sunk) {
    const ship = own.ships.querySelector(`[data-name="${sunk.name}"]`);
    if (ship) ship.classList.add('sinking');
    BS.bubbles(own.fx, sunk.cells);
    sunk.cells.forEach(([cx, cy]) => {
      const m = own.marks.querySelector(`[data-key="${cx},${cy}"]`);
      if (m) m.classList.add('dead');
    });
    BS.toast(own.sea, pretty(sunk.name) + ' lost', true);
    document.getElementById('of-' + sunk.name).classList.add('sunk');
    log('AI', 'sank your ' + pretty(sunk.name), 'sunk');
    await sleep(950);
  }

  async function aiAim(tx, ty) {
    // Radar sweep, then the reticle hops across a couple of cells before locking on
    await sleep(300);
    for (let i = 0; i < 2; i++) {
      const rx = Math.max(0, Math.min(N - 1, tx + Math.round((Math.random() - 0.5) * 6)));
      const ry = Math.max(0, Math.min(N - 1, ty + Math.round((Math.random() - 0.5) * 6)));
      const el = document.createElement('div');
      el.className = 'fx enemy';
      el.style.setProperty('--x', rx);
      el.style.setProperty('--y', ry);
      el.innerHTML = '<i class="lock"></i>';
      own.fx.appendChild(el);
      await sleep(190);
      el.remove();
    }
  }

  /* ---------- a full turn ---------- */
  async function fire(x, y, cell) {
    if (busy || over || cell.classList.contains('shot')) return;
    busy = true;
    enemy.root.classList.remove('targetable');
    enemy.root.classList.add('locked');

    const request = fetch(`/attack?x=${x}&y=${y}`).then((r) => r.json());
    const [data] = await Promise.all([request, sleep(0)]);
    if (data.error) {
      log('SYS', data.error, '');
      busy = false;
      setTurn(over ? 'over' : 'you');
      return;
    }

    // Player's shot
    stats.shots++;
    if (data.hit) stats.hits++;
    await impact(enemy, x, y, data.hit, false);
    log('YOU', `${label(x, y)} - ${data.hit ? 'hit!' : 'miss'}`, data.hit ? 'hit' : 'miss');
    updateStats();
    await sleep(data.hit ? 500 : 300);
    if (data.sunk) await sinkEnemy(data.sunk);

    // AI's shot
    if (data.AI_Turn) {
      const [ax, ay] = data.AI_Turn;
      setTurn('enemy');
      await aiAim(ax, ay);
      await impact(own, ax, ay, data.ai_hit, true);
      log('AI', `${label(ax, ay)} - ${data.ai_hit ? 'hit!' : 'miss'}`, data.ai_hit ? 'hit' : 'miss');
      if (data.ai_hit) {
        const name = GAME.board[ay][ax];
        ownHp[name]--;
        const li = flashRow('of-' + name);
        const pips = li.querySelectorAll('.hp i');
        pips[ownShips[name].length - ownHp[name] - 1].classList.add('dmg');
      }
      await sleep(data.ai_hit ? 500 : 250);
      if (data.ai_sunk) await sinkOwn(data.ai_sunk);
    }

    if (data.finished) {
      over = true;
      (data.reveal || []).forEach((s) => sinkEnemy(s, true));
      setTurn('over');
      await sleep(700);
      showEnd(data.finished === 'You Win!');
    } else {
      setTurn('you');
    }
    busy = false;
  }

  function showEnd(win) {
    const m = document.getElementById('modal');
    m.className = 'modal ' + (win ? 'win' : 'lose');
    document.getElementById('modalTitle').textContent = win ? 'VICTORY' : 'DEFEAT';
    document.getElementById('modalKicker').textContent = win ? 'Enemy fleet destroyed' : 'Your fleet was sunk';
    document.getElementById('modalText').textContent = win
      ? `You beat the ${DIFF[GAME.difficulty] || 'AI'} in ${stats.shots} shots.`
      : `The ${DIFF[GAME.difficulty] || 'AI'} found every ship. Its remaining fleet is now shown on the enemy grid.`;
    document.getElementById('mShots').textContent = stats.shots;
    document.getElementById('mHits').textContent = stats.hits;
    document.getElementById('mAcc').textContent = updateStats();
    m.hidden = false;
  }
  document.getElementById('modalClose').addEventListener('click', () => { document.getElementById('modal').hidden = true; });

  setTurn('you');
  log('SYS', 'Fleets deployed. Fire when ready.', '');
})();
