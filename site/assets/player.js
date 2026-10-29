/* Oriveda intro: a small timeline player.
 *
 * Each <section class="scene"> is a chapter with a duration. Inside it, any
 * element with data-at="<seconds>" gets the class "on" once the chapter's
 * clock reaches that time (and loses it again at data-out, if given). CSS
 * does the animating, so seeking anywhere is just "recompute which elements
 * are on": scrubbing backwards, skipping chapters and deep links all work
 * without replaying anything.
 *
 *   data-type="<chars/s>"   types the element's text out from data-at
 *   data-class="<name>"     a marker: while on, adds <name> to data-target
 *                           (a selector) or, by default, to its scene
 *   data-read="hide|skip"   in Read mode, hide the element / don't apply it
 */
(() => {
  'use strict';

  const root = document.documentElement;
  const $ = (sel) => document.querySelector(sel);
  const reduceMotion = matchMedia('(prefers-reduced-motion: reduce)').matches;

  // ---------- Build the chapter model ----------

  let total = 0;
  const chapters = [...document.querySelectorAll('#stage .scene')].map((el, i) => {
    const dur = parseFloat(el.dataset.duration) || 10;
    const timed = [...el.querySelectorAll('[data-at]')].map((node) => ({
      node,
      at: parseFloat(node.dataset.at),
      out: node.dataset.out ? parseFloat(node.dataset.out) : Infinity,
      read: node.dataset.read || '',
      cls: node.dataset.class || null,
      target: node.dataset.class ? (node.dataset.target ? el.querySelector(node.dataset.target) : el) : null,
      on: null,
    }));
    const typed = timed
      .filter((t) => t.node.hasAttribute('data-type'))
      .map((t) => ({ node: t.node, at: t.at, cps: parseFloat(t.node.dataset.type) || 30, full: t.node.textContent, shown: -1 }));
    const ch = { el, i, id: el.id, title: el.dataset.title, start: total, dur, timed, typed };
    total += dur;
    return ch;
  });

  // Returns the last visual element that just appeared, if any.
  const setScene = (ch, local, readMode) => {
    let revealed = null;
    for (const t of ch.timed) {
      const on = readMode ? t.read === '' : local >= t.at && local < t.out;
      if (on === t.on) continue;
      t.on = on;
      t.node.classList.toggle('on', on);
      if (t.target) t.target.classList.toggle(t.cls, on);
      if (on && !t.cls && !t.node.closest('.caps')) revealed = t.node;
    }
    for (const ty of ch.typed) {
      const n = readMode ? ty.full.length : Math.max(0, Math.min(ty.full.length, Math.floor((local - ty.at) * ty.cps)));
      if (n === ty.shown) continue;
      ty.shown = n;
      ty.node.textContent = ty.full.slice(0, n);
      ty.node.classList.toggle('typing', !readMode && n < ty.full.length && local >= ty.at);
    }
    return revealed;
  };

  // On small screens a scene can be taller than the stage. Scroll it so
  // whatever just appeared is in view above the captions, like a camera.
  const follow = (scene, node) => {
    if (scene.scrollHeight <= scene.clientHeight) return;
    const s = scene.getBoundingClientRect();
    const r = node.getBoundingClientRect();
    const bottom = s.bottom - 110;
    if (r.bottom <= bottom) return;
    const delta = r.height > bottom - s.top - 16 ? r.top - s.top - 16 : r.bottom - bottom;
    scene.scrollBy({ top: delta, behavior: reduceMotion ? 'auto' : 'smooth' });
  };

  // ---------- Player state ----------

  let t = 0;
  let playing = false;
  let ended = false;
  let rate = 1;
  let current = -1;
  let dirty = true;
  let readMode = root.classList.contains('read');
  const RATES = [1, 1.25, 1.5, 2, 0.75];

  const chapterAt = (time) => {
    for (let i = chapters.length - 1; i >= 0; i--) if (time >= chapters[i].start) return i;
    return 0;
  };

  const fmt = (s) => {
    s = Math.max(0, Math.floor(s));
    return `${Math.floor(s / 60)}:${String(s % 60).padStart(2, '0')}`;
  };

  // ---------- Controls UI ----------

  const timeline = $('#timeline');
  const tip = $('#tip');
  const labels = $('#chapter-labels');
  const menu = $('#chapter-menu');
  const keys = $('#keys');
  const toc = $('#toc');
  const timeEl = $('#time');
  const nowTitle = $('#now-title');
  const btnPlay = $('#btn-play');
  const flashEl = $('#flash');

  for (const ch of chapters) {
    const seg = document.createElement('div');
    seg.className = 'seg';
    seg.style.flex = `${ch.dur} 1 0`;
    seg.innerHTML = '<span class="seg-fill"></span>';
    timeline.insertBefore(seg, tip);
    ch.seg = seg;
    ch.fill = seg.firstChild;

    const label = document.createElement('button');
    label.type = 'button';
    label.style.flex = `${ch.dur} 1 0`;
    label.textContent = ch.title;
    label.title = `${ch.i + 1}. ${ch.title}`;
    label.addEventListener('click', () => goChapter(ch.i));
    labels.appendChild(label);
    ch.label = label;

    const li = document.createElement('li');
    li.innerHTML = `<button type="button"><span class="n">${ch.i + 1}</span><span></span><span class="d">${fmt(ch.start)}</span></button>`;
    li.querySelector('span:nth-child(2)').textContent = ch.title;
    li.firstChild.addEventListener('click', () => { goChapter(ch.i); closePopovers(); });
    menu.appendChild(li);
    ch.menuItem = li.firstChild;

    const a = document.createElement('a');
    a.href = `#${ch.id}`;
    a.textContent = ch.title;
    toc.appendChild(a);
    ch.tocLink = a;
  }
  timeline.setAttribute('aria-valuemax', String(Math.round(total)));

  const setCurrent = (idx) => {
    if (idx === current) return;
    const prev = chapters[current];
    current = idx;
    const ch = chapters[idx];
    if (prev && !readMode) prev.el.classList.remove('active');
    if (!readMode) {
      ch.el.classList.add('active');
      ch.el.scrollTop = 0;
    }
    for (const c of chapters) {
      const isCur = c === ch;
      c.seg.classList.toggle('active', isCur);
      c.label.setAttribute('aria-current', String(isCur));
      c.menuItem.setAttribute('aria-current', String(isCur));
      c.tocLink.setAttribute('aria-current', String(isCur));
    }
    nowTitle.textContent = `${idx + 1} / ${chapters.length} · ${ch.title}`;
    syncHash();
  };

  // Writing the hash before the page has loaded makes the browser jump to it
  // on load, so wait until then.
  let loaded = document.readyState === 'complete';
  const syncHash = () => {
    if (loaded && current >= 0) history.replaceState(null, '', `${location.pathname}${location.search}#${chapters[current].id}`);
  };
  addEventListener('load', () => { loaded = true; syncHash(); });

  const render = () => {
    dirty = false;
    const idx = chapterAt(t);
    setCurrent(idx);
    const ch = chapters[idx];
    const revealed = setScene(ch, t - ch.start, false);
    if (revealed && !dragging) follow(ch.el, revealed);
    for (const c of chapters) c.fill.style.width = `${Math.min(1, Math.max(0, (t - c.start) / c.dur)) * 100}%`;
    timeEl.textContent = `${fmt(t)} / ${fmt(total)}`;
    timeline.setAttribute('aria-valuenow', String(Math.round(t)));
    timeline.setAttribute('aria-valuetext', `${fmt(t)}, ${ch.title}`);
  };

  const setPlaying = (p) => {
    playing = p;
    root.classList.toggle('paused', !p);
    root.classList.toggle('ended', ended && !p);
    btnPlay.setAttribute('aria-label', p ? 'Pause' : ended ? 'Replay' : 'Play');
  };

  const seek = (time) => {
    const leaving = chapters[current];
    t = Math.min(Math.max(0, time), total);
    // Chapters other than the one we land on go back to their starting state,
    // so returning to one replays it instead of showing it frozen mid-way.
    const idx = chapterAt(t);
    if (leaving && leaving.i !== idx) setScene(leaving, -1, false);
    if (ended && t < total) { ended = false; setPlaying(playing); }
    dirty = true;
  };

  const goChapter = (i) => {
    if (readMode) {
      chapters[i].el.scrollIntoView({ behavior: reduceMotion ? 'auto' : 'smooth' });
      return;
    }
    seek(chapters[Math.max(0, Math.min(chapters.length - 1, i))].start);
    if (!playing) setPlaying(true);
  };

  const togglePlay = () => {
    if (ended) { ended = false; seek(0); setPlaying(true); }
    else setPlaying(!playing);
    flash(playing ? 'play' : 'pause');
  };

  const flash = (kind) => {
    flashEl.className = `flash ${kind}`;
    void flashEl.offsetWidth;
    flashEl.classList.add('show');
  };

  const prevChapter = () => {
    const ch = chapters[current];
    goChapter(t - ch.start > 2 ? current : current - 1);
  };
  const nextChapter = () => { if (current < chapters.length - 1) goChapter(current + 1); };

  // ---------- Clock ----------

  let last = null;
  const frame = (now) => {
    if (playing && !readMode) {
      if (last !== null) t += Math.min(0.1, (now - last) / 1000) * rate;
      if (t >= total) {
        t = total;
        ended = true;
        setPlaying(false);
      }
      dirty = true;
    }
    last = now;
    if (dirty && !readMode) render();
    requestAnimationFrame(frame);
  };

  // ---------- Timeline scrubbing ----------

  const timeFromX = (x) => {
    for (const ch of chapters) {
      const r = ch.seg.getBoundingClientRect();
      if (x <= r.right + 1.5 || ch === chapters[chapters.length - 1]) {
        return ch.start + Math.min(1, Math.max(0, (x - r.left) / r.width)) * ch.dur;
      }
    }
    return 0;
  };

  let dragging = false;
  timeline.addEventListener('pointerdown', (e) => {
    dragging = true;
    timeline.classList.add('dragging');
    timeline.setPointerCapture(e.pointerId);
    seek(timeFromX(e.clientX));
  });
  timeline.addEventListener('pointermove', (e) => {
    const time = timeFromX(e.clientX);
    const box = timeline.getBoundingClientRect();
    tip.hidden = false;
    tip.textContent = `${fmt(time)} · ${chapters[chapterAt(time)].title}`;
    tip.style.left = `${Math.min(box.width - 70, Math.max(70, e.clientX - box.left))}px`;
    if (dragging) seek(time);
  });
  const endDrag = () => { dragging = false; timeline.classList.remove('dragging'); };
  timeline.addEventListener('pointerup', endDrag);
  timeline.addEventListener('pointercancel', endDrag);
  timeline.addEventListener('pointerleave', () => { if (!dragging) tip.hidden = true; });

  // ---------- Buttons ----------

  // Mouse clicks shouldn't leave focus on a control, or the next Space press
  // would activate that button instead of toggling playback.
  document.querySelectorAll('.controls button').forEach((b) => b.addEventListener('mousedown', (e) => e.preventDefault()));

  btnPlay.addEventListener('click', togglePlay);
  $('#btn-prev').addEventListener('click', prevChapter);
  $('#btn-next').addEventListener('click', nextChapter);

  const btnCc = $('#btn-cc');
  const toggleCaptions = () => {
    const on = root.classList.toggle('no-cc');
    btnCc.setAttribute('aria-pressed', String(!on));
  };
  btnCc.addEventListener('click', toggleCaptions);

  const btnSpeed = $('#btn-speed');
  const cycleSpeed = () => {
    rate = RATES[(RATES.indexOf(rate) + 1) % RATES.length];
    btnSpeed.textContent = `${rate}×`;
  };
  btnSpeed.addEventListener('click', cycleSpeed);

  const toggleFullscreen = () => {
    if (document.fullscreenElement) document.exitFullscreen();
    else root.requestFullscreen?.().catch(() => {});
  };
  $('#btn-fs').addEventListener('click', toggleFullscreen);

  const btnChapters = $('#btn-chapters');
  const btnKeys = $('#btn-keys');
  const popovers = [[btnChapters, menu], [btnKeys, keys]];
  const closePopovers = () => popovers.forEach(([b, p]) => { p.hidden = true; b.setAttribute('aria-expanded', 'false'); });
  for (const [btn, pop] of popovers) {
    btn.addEventListener('click', (e) => {
      e.stopPropagation();
      const open = pop.hidden;
      closePopovers();
      pop.hidden = !open;
      btn.setAttribute('aria-expanded', String(open));
    });
  }
  document.addEventListener('click', (e) => { if (!e.target.closest('.popover')) closePopovers(); });

  // Clicking the stage itself plays/pauses, like a video.
  $('#stage').addEventListener('click', (e) => {
    if (readMode || e.target.closest('a, button, pre, .prompt')) return;
    if (String(getSelection())) return;
    togglePlay();
  });

  document.querySelectorAll('[data-copy]').forEach((btn) => {
    btn.addEventListener('click', async () => {
      const text = document.querySelector(btn.dataset.copy).textContent;
      try {
        await navigator.clipboard.writeText(text);
        btn.textContent = 'Copied';
      } catch {
        const range = document.createRange();
        range.selectNodeContents(document.querySelector(btn.dataset.copy));
        getSelection().removeAllRanges();
        getSelection().addRange(range);
        btn.textContent = 'Press Ctrl+C';
      }
      setTimeout(() => { btn.textContent = 'Copy'; }, 1800);
    });
  });

  // ---------- Watch / Read modes ----------

  const btnWatch = $('#mode-watch');
  const btnRead = $('#mode-read');

  // In Read mode, track the chapter in view so the header and hash follow along.
  const spy = new IntersectionObserver((entries) => {
    if (!readMode) return;
    const visible = entries.filter((e) => e.isIntersecting).sort((a, b) => a.boundingClientRect.top - b.boundingClientRect.top)[0];
    if (visible) setCurrent(chapters.findIndex((c) => c.el === visible.target));
  }, { rootMargin: '-45% 0px -50% 0px' });
  chapters.forEach((c) => spy.observe(c.el));

  const setMode = (read) => {
    const idx = readMode ? Math.max(0, current) : chapterAt(t);
    readMode = read;
    root.classList.toggle('read', read);
    root.classList.toggle('watch', !read);
    btnWatch.setAttribute('aria-pressed', String(!read));
    btnRead.setAttribute('aria-pressed', String(read));
    const url = new URL(location.href);
    if (read) url.searchParams.set('read', ''); else url.searchParams.delete('read');
    history.replaceState(null, '', url.toString().replace('?read=', '?read'));
    closePopovers();

    if (read) {
      setPlaying(false);
      chapters.forEach((c) => { c.el.classList.remove('active'); setScene(c, Infinity, true); });
      setCurrent(idx);
      chapters[idx].el.scrollIntoView();
    } else {
      chapters.forEach((c) => setScene(c, -1, false));
      window.scrollTo(0, 0);
      current = -1;
      seek(chapters[idx].start);
      render();
      setPlaying(true);
    }
  };
  btnWatch.addEventListener('click', () => { if (readMode) setMode(false); });
  btnRead.addEventListener('click', () => { if (!readMode) setMode(true); });

  // ---------- Keyboard ----------

  document.addEventListener('keydown', (e) => {
    if (e.ctrlKey || e.metaKey || e.altKey) return;
    if (e.target.closest('input, textarea, select, [contenteditable]')) return;
    const k = e.key;
    if (k === 'r' || k === 'R') { setMode(!readMode); return; }
    if (k === 'Escape') { closePopovers(); return; }
    if (readMode) return;
    const onButton = e.target.closest('button, a');
    if ((k === ' ' || k === 'Enter') && onButton) return;

    if (k === ' ' || k === 'k' || k === 'K') togglePlay();
    else if (k === 'ArrowLeft') seek(t - 5);
    else if (k === 'ArrowRight') seek(t + 5);
    else if (k === 'Home') seek(0);
    else if (k === 'End') seek(total);
    else if (k === 'p' || k === 'P') prevChapter();
    else if (k === 'n' || k === 'N') nextChapter();
    else if (/^[1-9]$/.test(k) && +k <= chapters.length) goChapter(+k - 1);
    else if (k === 'c' || k === 'C') toggleCaptions();
    else if (k === 's' || k === 'S') cycleSpeed();
    else if (k === 'f' || k === 'F') toggleFullscreen();
    else if (k === '?') btnKeys.click();
    else return;
    e.preventDefault();
  });

  window.addEventListener('hashchange', () => {
    const i = chapters.findIndex((c) => `#${c.id}` === location.hash);
    if (i >= 0 && !readMode) goChapter(i);
  });

  // Keep captions clear of the controls bar, whatever height it wraps to.
  new ResizeObserver(([entry]) => {
    root.style.setProperty('--controls-h', `${Math.ceil(entry.borderBoxSize?.[0]?.blockSize ?? entry.target.offsetHeight)}px`);
  }).observe($('#controls'));

  // ---------- Starfield ----------

  const sky = $('#sky');
  const ctx = sky.getContext('2d');
  let stars = [];
  let sw = 0;
  let sh = 0;
  const resizeSky = () => {
    const dpr = Math.min(2, window.devicePixelRatio || 1);
    sw = innerWidth;
    sh = innerHeight;
    sky.width = sw * dpr;
    sky.height = sh * dpr;
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    stars = Array.from({ length: Math.round((sw * sh) / 5200) }, () => ({
      x: Math.random() * sw,
      y: Math.random() * sh,
      r: Math.random() * 1.1 + 0.15,
      p: Math.random() * Math.PI * 2,
      s: 0.4 + Math.random() * 1.4,
    }));
    drawSky(0);
  };
  const drawSky = (now) => {
    ctx.clearRect(0, 0, sw, sh);
    ctx.fillStyle = '#d6defa';
    for (const s of stars) {
      ctx.globalAlpha = reduceMotion ? 0.5 : 0.3 + 0.35 * Math.sin(s.p + (now / 1000) * s.s);
      ctx.beginPath();
      ctx.arc(s.x, s.y, s.r, 0, Math.PI * 2);
      ctx.fill();
    }
  };
  let lastSky = 0;
  const skyLoop = (now) => {
    if (now - lastSky > 50) { drawSky(now); lastSky = now; }
    requestAnimationFrame(skyLoop);
  };
  addEventListener('resize', resizeSky);
  resizeSky();
  if (!reduceMotion) requestAnimationFrame(skyLoop);

  // ---------- Start ----------

  const startIdx = Math.max(0, chapters.findIndex((c) => `#${c.id}` === location.hash));
  // ?t=<seconds> starts at a timestamp, like a video link.
  const startT = parseFloat(new URLSearchParams(location.search).get('t'));
  if (readMode) {
    btnWatch.setAttribute('aria-pressed', 'false');
    btnRead.setAttribute('aria-pressed', 'true');
    setPlaying(false);
    chapters.forEach((c) => setScene(c, Infinity, true));
    setCurrent(startIdx);
    if (location.hash) chapters[startIdx].el.scrollIntoView();
  } else {
    chapters.forEach((c) => setScene(c, -1, false));
    seek(Number.isFinite(startT) ? startT : chapters[startIdx].start);
    render();
    setPlaying(true);
  }
  requestAnimationFrame(frame);
})();
