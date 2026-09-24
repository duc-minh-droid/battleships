/* Ship placement: drag from the dock, snap to the grid, rotate, randomise. */
(function () {
  const { buildBoard, makeShip, pretty, sleep } = window.BS;
  const N = GAME.size;
  const NOTES = {
    easy: 'Random ship layout, random shots. A relaxed first game.',
    hard: 'The original coursework AI: follows up hits in a direction and reverses along a line.',
    expert: 'Hunt/target AI: probability-density search, then finishes every ship it touches.',
  };

  // Largest first, like the original template
  const fleet = Object.entries(GAME.ships)
    .sort((a, b) => b[1] - a[1])
    .map(([name, len]) => ({ name, len, x: 0, y: 0, v: false, placed: false }));

  const board = buildBoard(document.getElementById('board'), N);
  const dock = document.getElementById('dock');
  const startBtn = document.getElementById('startBtn');
  let lastTouched = null;
  let drag = null;

  /* ---------- rules ---------- */
  function cellsOf(s, x = s.x, y = s.y, v = s.v) {
    return Array.from({ length: s.len }, (_, i) => (v ? [x, y + i] : [x + i, y]));
  }
  function fits(s, x, y, v) {
    const cells = cellsOf(s, x, y, v);
    if (cells.some(([cx, cy]) => cx < 0 || cy < 0 || cx >= N || cy >= N)) return false;
    const taken = new Set();
    fleet.forEach((o) => { if (o !== s && o.placed) cellsOf(o).forEach(([a, b]) => taken.add(a + ',' + b)); });
    return cells.every(([cx, cy]) => !taken.has(cx + ',' + cy));
  }

  /* ---------- rendering ---------- */
  function render(settleName) {
    board.ships.innerHTML = '';
    dock.innerHTML = '';
    fleet.forEach((s) => {
      if (s.placed) {
        const el = makeShip(s.name, s.len, s.x, s.y, s.v, s.name === settleName ? 'settle' : '');
        attach(el, s);
        board.ships.appendChild(el);
      }
      const slot = document.createElement('div');
      slot.className = 'dock-slot' + (s.placed ? ' placed' : '');
      slot.innerHTML = `<div class="ship-holder"></div><div class="meta"><b>${pretty(s.name)}</b>` +
        `<span class="pips">${'<i></i>'.repeat(s.len)}</span></div>`;
      const el = makeShip(s.name, s.len, 0, 0, false, s.placed ? 'parked' : '');
      if (!s.placed) attach(el, s);
      slot.firstChild.appendChild(el);
      dock.appendChild(slot);
    });
    const count = fleet.filter((s) => s.placed).length;
    document.getElementById('placedCount').textContent = count;
    document.getElementById('totalCount').textContent = fleet.length;
    startBtn.disabled = count !== fleet.length;
  }

  /* ---------- dragging ---------- */
  function attach(el, s) {
    el.addEventListener('pointerdown', (e) => {
      if (e.button !== 0) return;
      e.preventDefault();
      const r = el.getBoundingClientRect();
      const along = s.v ? (e.clientY - r.top) / r.height : (e.clientX - r.left) / r.width;
      drag = { s, el, grab: Math.min(s.len - 1, Math.floor(along * s.len)), sx: e.clientX, sy: e.clientY, moving: false, v: s.v };
      lastTouched = s;
    });
  }

  function ensureGhost() {
    if (drag.ghost) drag.ghost.remove();
    const g = document.createElement('div');
    g.className = 'drag-ghost';
    g.style.setProperty('--cell', board.cellSize() + 'px');
    g.appendChild(makeShip(drag.s.name, drag.s.len, 0, 0, drag.v));
    document.body.appendChild(g);
    drag.ghost = g;
  }

  function preview(show, x, y, ok) {
    let p = board.fx.querySelector('.preview');
    if (!show) { if (p) p.remove(); return; }
    if (!p) { p = document.createElement('div'); p.className = 'preview'; board.fx.appendChild(p); }
    p.style.setProperty('--x', x);
    p.style.setProperty('--y', y);
    p.style.setProperty('--w', drag.v ? 1 : drag.s.len);
    p.style.setProperty('--h', drag.v ? drag.s.len : 1);
    p.classList.toggle('bad', !ok);
  }

  function update(e) {
    const c = board.cellSize();
    const px = e ? e.clientX : drag.lx;
    const py = e ? e.clientY : drag.ly;
    drag.lx = px; drag.ly = py;
    const gx = px - (drag.v ? 0.5 : drag.grab + 0.5) * c;
    const gy = py - (drag.v ? drag.grab + 0.5 : 0.5) * c;
    drag.ghost.style.left = gx + 'px';
    drag.ghost.style.top = gy + 'px';
    const r = board.grid.getBoundingClientRect();
    const x = Math.round((gx - r.left) / c);
    const y = Math.round((gy - r.top) / c);
    const inside = px > r.left - c && px < r.right + c && py > r.top - c && py < r.bottom + c;
    if (!inside) { drag.target = null; preview(false); return; }
    const cx = Math.max(0, Math.min(N - (drag.v ? 1 : drag.s.len), x));
    const cy = Math.max(0, Math.min(N - (drag.v ? drag.s.len : 1), y));
    const ok = fits(drag.s, cx, cy, drag.v);
    drag.target = ok ? { x: cx, y: cy } : null;
    preview(true, cx, cy, ok);
  }

  window.addEventListener('pointermove', (e) => {
    if (!drag) return;
    if (!drag.moving) {
      if (Math.hypot(e.clientX - drag.sx, e.clientY - drag.sy) < 5) return;
      drag.moving = true;
      document.body.classList.add('dragging');
      drag.el.style.opacity = '.2';
      ensureGhost();
    }
    update(e);
  });

  window.addEventListener('pointerup', () => {
    if (!drag) return;
    const d = drag;
    drag = null;
    document.body.classList.remove('dragging');
    if (d.ghost) d.ghost.remove();
    preview(false);
    if (!d.moving) {
      if (d.s.placed) rotateInPlace(d.s);
      return;
    }
    if (d.target) {
      Object.assign(d.s, { x: d.target.x, y: d.target.y, v: d.v, placed: true });
      render(d.s.name);
    } else {
      render();
    }
  });

  function rotateDrag() {
    drag.v = !drag.v;
    drag.grab = Math.min(drag.grab, drag.s.len - 1);
    ensureGhost();
    update();
  }
  window.addEventListener('contextmenu', (e) => { if (drag && drag.moving) { e.preventDefault(); rotateDrag(); } });
  window.addEventListener('keydown', (e) => {
    if (e.key !== 'r' && e.key !== 'R') return;
    if (drag && drag.moving) rotateDrag();
    else if (lastTouched && lastTouched.placed) rotateInPlace(lastTouched);
  });

  function rotateInPlace(s) {
    if (fits(s, s.x, s.y, !s.v)) {
      s.v = !s.v;
      render();
      // re-trigger the CSS rotation transition from the old orientation
      const el = board.ships.querySelector(`[data-name="${s.name}"]`);
      const svg = el.querySelector('svg');
      svg.style.transition = 'none';
      svg.style.transform = s.v ? 'none' : 'rotate(90deg) translate(0,-100%)';
      void svg.offsetWidth;
      svg.style.transition = '';
      svg.style.transform = '';
    } else {
      const el = board.ships.querySelector(`[data-name="${s.name}"]`);
      el.classList.remove('shake'); void el.offsetWidth; el.classList.add('shake');
    }
  }

  /* ---------- buttons ---------- */
  async function randomise() {
    fleet.forEach((s) => { s.placed = false; });
    render();
    for (const s of fleet) {
      for (let tries = 0; tries < 500; tries++) {
        const v = Math.random() < 0.5;
        const x = Math.floor(Math.random() * N);
        const y = Math.floor(Math.random() * N);
        if (fits(s, x, y, v)) { Object.assign(s, { x, y, v, placed: true }); break; }
      }
      render(s.name);
      await sleep(110);
    }
  }
  document.getElementById('randomBtn').addEventListener('click', randomise);
  document.getElementById('clearBtn').addEventListener('click', () => { fleet.forEach((s) => { s.placed = false; }); render(); });

  const radios = document.querySelectorAll('input[name=difficulty]');
  function setDifficulty(d) {
    radios.forEach((r) => { r.checked = r.value === d; });
    document.getElementById('diffNote').textContent = NOTES[d];
  }
  radios.forEach((r) => r.addEventListener('change', () => setDifficulty(r.value)));
  setDifficulty(GAME.difficulty || 'hard');

  startBtn.addEventListener('click', async () => {
    const placement = {};
    fleet.forEach((s) => { placement[s.name] = [String(s.x), String(s.y), s.v ? 'v' : 'h']; });
    const difficulty = document.querySelector('input[name=difficulty]:checked').value;
    startBtn.disabled = true;
    startBtn.textContent = 'Deploying...';
    const res = await fetch(window.location.pathname, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ placement, difficulty }),
    });
    if (res.ok) {
      document.querySelector('main').style.transition = 'opacity .35s, transform .35s';
      document.querySelector('main').style.opacity = '0';
      document.querySelector('main').style.transform = 'translateY(-8px)';
      setTimeout(() => { window.location.href = '/'; }, 350);
    } else {
      startBtn.textContent = 'Start battle';
      startBtn.disabled = false;
      alert('The server rejected that placement.');
    }
  });

  /* ---------- initial state ---------- */
  if (GAME.placement) {
    fleet.forEach((s) => {
      const p = GAME.placement[s.name];
      if (p) Object.assign(s, { x: +p[0], y: +p[1], v: p[2] === 'v', placed: true });
    });
  }
  render();
})();
