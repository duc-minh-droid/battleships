/* Shared board, ship and effect helpers for both pages. */
(function () {
  const LETTERS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ';
  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
  const label = (x, y) => LETTERS[x] + (y + 1);
  const pretty = (name) => name.replace(/_/g, ' ');

  /* ---------- board ---------- */
  function buildBoard(root, n, onCell) {
    root.classList.add('board');
    root.style.setProperty('--n', n);
    root.innerHTML = '';
    const cols = document.createElement('div');
    cols.className = 'cols';
    const rows = document.createElement('div');
    rows.className = 'rows';
    for (let i = 0; i < n; i++) {
      cols.insertAdjacentHTML('beforeend', `<span>${LETTERS[i]}</span>`);
      rows.insertAdjacentHTML('beforeend', `<span>${i + 1}</span>`);
    }
    const sea = document.createElement('div');
    sea.className = 'sea';
    const grid = document.createElement('div');
    grid.className = 'grid';
    const cells = [];
    for (let y = 0; y < n; y++) {
      for (let x = 0; x < n; x++) {
        const c = document.createElement('div');
        c.className = 'cell';
        c.dataset.x = x;
        c.dataset.y = y;
        c.setAttribute('aria-label', label(x, y));
        if (onCell) c.addEventListener('click', () => onCell(x, y, c));
        grid.appendChild(c);
        cells.push(c);
      }
    }
    const ships = document.createElement('div');
    ships.className = 'layer ships-layer';
    const marks = document.createElement('div');
    marks.className = 'layer';
    const fx = document.createElement('div');
    fx.className = 'layer';
    sea.append(grid, ships, marks, fx);
    root.append(document.createElement('span'), cols, rows, sea);
    return {
      root, sea, grid, ships, marks, fx, n,
      cell: (x, y) => cells[y * n + x],
      cellSize: () => grid.getBoundingClientRect().width / n,
    };
  }

  /* ---------- ship artwork ---------- */
  function turret(cx, cy, r, dir) {
    const bx = dir > 0 ? cx : cx - r * 2.2;
    return `<g class="detail"><rect x="${bx}" y="${cy - 3}" width="${r * 2.2}" height="6" rx="2" fill="#2b3540"/>` +
      `<circle cx="${cx}" cy="${cy}" r="${r}" fill="#6f7d8c" stroke="#2b3540" stroke-width="3"/></g>`;
  }

  function shipSVG(name, len) {
    const L = len * 100;
    const id = 'g' + Math.random().toString(36).slice(2, 8);
    const defs = `<defs><linearGradient id="${id}" x1="0" y1="0" x2="0" y2="1">` +
      `<stop offset="0" stop-color="#a7b4c2"/><stop offset=".5" stop-color="#6d7b8a"/><stop offset="1" stop-color="#46525f"/></linearGradient></defs>`;
    let hull, deck, details = '';
    if (name === 'Submarine') {
      hull = `M 14 50 C 14 26 40 24 80 26 L ${L - 70} 26 C ${L - 18} 28 ${L - 8} 40 ${L - 8} 50 C ${L - 8} 60 ${L - 18} 72 ${L - 70} 74 L 80 74 C 40 76 14 74 14 50 Z`;
      deck = `M 40 50 C 40 38 60 38 90 38 L ${L - 80} 38 C ${L - 40} 40 ${L - 34} 46 ${L - 34} 50 C ${L - 34} 54 ${L - 40} 60 ${L - 80} 62 L 90 62 C 60 62 40 62 40 50 Z`;
      details = `<g class="detail"><rect x="${L * 0.42}" y="34" width="${L * 0.14}" height="32" rx="12" fill="#39444f" stroke="#222b33" stroke-width="3"/>` +
        `<rect x="${L * 0.47}" y="16" width="5" height="20" fill="#222b33"/></g>`;
    } else {
      hull = `M 10 24 Q 4 50 10 76 L ${L * 0.78} 80 Q ${L - 14} 70 ${L - 4} 50 Q ${L - 14} 30 ${L * 0.78} 20 Z`;
      deck = `M 22 34 Q 18 50 22 66 L ${L * 0.76} 68 Q ${L - 34} 62 ${L - 22} 50 Q ${L - 34} 38 ${L * 0.76} 32 Z`;
      if (name === 'Aircraft_Carrier') {
        deck = `M 18 28 L ${L - 60} 28 Q ${L - 24} 34 ${L - 18} 50 Q ${L - 24} 66 ${L - 60} 72 L 18 72 Z`;
        details = `<g class="detail"><line x1="40" y1="50" x2="${L - 70}" y2="50" stroke="#e8eef5" stroke-width="3" stroke-dasharray="22 16" opacity=".75"/>` +
          `<line x1="40" y1="40" x2="${L * 0.55}" y2="32" stroke="#e8eef5" stroke-width="2" opacity=".35"/>` +
          `<rect x="${L * 0.6}" y="62" width="${L * 0.1}" height="16" rx="3" fill="#39444f" stroke="#222b33" stroke-width="2"/></g>`;
      } else {
        const bridge = `<g class="detail"><rect x="${L * 0.44}" y="38" width="${Math.max(38, L * 0.12)}" height="24" rx="4" fill="#4b5763" stroke="#222b33" stroke-width="3"/>` +
          `<rect x="${L * 0.44 + 8}" y="44" width="10" height="12" rx="2" fill="#9fd8ff" opacity=".7"/></g>`;
        let turrets = [];
        if (name === 'Battleship') turrets = [[L * 0.2, -1], [L * 0.32, -1], [L * 0.72, 1]];
        else if (name === 'Cruiser') turrets = [[L * 0.2, -1], [L * 0.74, 1]];
        else turrets = [[L * 0.72, 1]];
        details = bridge + turrets.map(([cx, d]) => turret(cx, 50, 11, d)).join('');
      }
    }
    return `<svg viewBox="0 0 ${L} 100" preserveAspectRatio="none" aria-hidden="true">${defs}` +
      `<path class="hull" d="${hull}" fill="url(#${id})" stroke="#1d252d" stroke-width="3"/>` +
      `<path class="deck" d="${deck}" fill="#7d8b99" opacity=".9"/>${details}</svg>`;
  }

  function makeShip(name, len, x, y, vertical, extra) {
    const el = document.createElement('div');
    el.className = 'ship' + (vertical ? ' v' : '') + (extra ? ' ' + extra : '');
    el.dataset.name = name;
    el.style.setProperty('--len', len);
    el.style.setProperty('--x', x);
    el.style.setProperty('--y', y);
    el.innerHTML = shipSVG(name, len);
    el.title = pretty(name) + ' (' + len + ')';
    return el;
  }

  /* ---------- effects ---------- */
  function fxAt(layer, x, y, cls) {
    const el = document.createElement('div');
    el.className = 'fx' + (cls ? ' ' + cls : '');
    el.style.setProperty('--x', x);
    el.style.setProperty('--y', y);
    layer.appendChild(el);
    return el;
  }
  function particles(el, cls, count, spread, extra) {
    for (let i = 0; i < count; i++) {
      const p = document.createElement('i');
      p.className = cls;
      const a = (Math.PI * 2 * i) / count + Math.random() * 0.6;
      const d = spread * (0.55 + Math.random() * 0.6);
      p.style.setProperty('--dx', Math.cos(a) * d + 'px');
      p.style.setProperty('--dy', Math.sin(a) * d + 'px');
      if (extra) extra(p, i);
      el.appendChild(p);
    }
  }
  async function incoming(layer, x, y, enemy) {
    const el = fxAt(layer, x, y, enemy ? 'enemy' : '');
    el.innerHTML = '<i class="lock"></i><i class="shadow"></i><i class="shell"></i>';
    await sleep(500);
    el.remove();
  }
  function splash(layer, x, y) {
    const el = fxAt(layer, x, y);
    el.innerHTML = '<i class="ring"></i><i class="ring"></i><i class="ring"></i><i class="column"></i>';
    particles(el, 'drop', 9, 26);
    setTimeout(() => el.remove(), 1300);
  }
  function explode(layer, x, y, board) {
    const el = fxAt(layer, x, y);
    el.innerHTML = '<i class="flash"></i>';
    particles(el, 'spark', 14, 44);
    particles(el, 'puff', 4, 16, (p, i) => { p.style.animationDelay = 0.1 + i * 0.08 + 's'; });
    if (board) {
      board.root.classList.remove('quake');
      void board.root.offsetWidth;
      board.root.classList.add('quake');
    }
    setTimeout(() => el.remove(), 1700);
  }
  function bubbles(layer, cells) {
    cells.forEach(([x, y], k) => {
      const el = fxAt(layer, x, y);
      particles(el, 'bubble', 4, 10, (p, i) => { p.style.animationDelay = k * 0.12 + i * 0.25 + 's'; });
      setTimeout(() => el.remove(), 3000);
    });
  }
  function mark(layer, x, y, kind) {
    const el = document.createElement('div');
    el.className = 'mark ' + kind;
    el.style.setProperty('--x', x);
    el.style.setProperty('--y', y);
    el.dataset.key = x + ',' + y;
    layer.appendChild(el);
    return el;
  }
  function toast(container, text, enemy) {
    const t = document.createElement('div');
    t.className = 'toast' + (enemy ? ' enemy' : '');
    t.textContent = text;
    container.appendChild(t);
    setTimeout(() => t.remove(), 2100);
  }

  window.BS = { LETTERS, sleep, label, pretty, buildBoard, shipSVG, makeShip, incoming, splash, explode, bubbles, mark, toast };
})();
