/* Oriveda intro: a timeline player whose every frame is a function of t.
 *
 * Each <section class="scene"> is a chapter with a duration. Inside it, an
 * element with data-at="<seconds>" gets a CSS variable --p that eases from
 * 0 to 1 over data-dur seconds (default 0.7) once the chapter's clock passes
 * data-at, and back to 0 after data-out. Nothing on the plate keeps its own
 * time (no CSS transitions or animations), so scrubbing, seeking and deep
 * links land on exactly the frame playback would have shown.
 *
 *   class="mask"            words rise through a mask, staggered
 *   class="draw"            an SVG stroke draws on (pathLength="1")
 *   data-type="<chars/s>"   types the element's text out
 *   data-mark="<name>"      a marker: writes its progress to --<name> on
 *                           data-target (a selector) or, by default, the scene
 *   data-ease="linear"      linear instead of ease-out
 *   data-read="hide|skip"   in Read mode, hide the element / don't apply it
 *
 * .caps > .cap lines are the narration: subtitles in Watch mode, a lede in
 * Read mode.
 */
(() => {
  'use strict';

  const root = document.documentElement;
  const $ = (sel) => document.querySelector(sel);
  const reduceMotion = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const clamp01 = (x) => (x < 0 ? 0 : x > 1 ? 1 : x);
  const EASES = { out: (x) => 1 - (1 - x) ** 3, linear: (x) => x };
  const NS = 'http://www.w3.org/2000/svg';

  // ---------- Prepare markup ----------

  document.querySelectorAll('.mask').forEach((el) => {
    const text = el.textContent.trim();
    el.setAttribute('aria-label', text);
    el.textContent = '';
    text.split(/\s+/).forEach((word, i) => {
      if (i) el.append(' ');
      const w = document.createElement('span');
      w.className = 'w';
      w.setAttribute('aria-hidden', 'true');
      const wi = document.createElement('span');
      wi.className = 'wi';
      wi.textContent = word;
      w.append(wi);
      el.append(w);
    });
  });

  // Change-frequency ticks: n marks spread along a time axis, seeded so they
  // land in the same places on every visit.
  document.querySelectorAll('svg.ticks').forEach((svg) => {
    const n = parseInt(svg.dataset.ticks, 10);
    let seed = parseInt(svg.dataset.seed, 10) || 1;
    const rnd = () => (seed = (seed * 16807) % 2147483647) / 2147483647;
    const line = (x1, y1, x2, y2, cls) => {
      const l = document.createElementNS(NS, 'line');
      Object.entries({ x1, y1, x2, y2 }).forEach(([k, v]) => l.setAttribute(k, v));
      l.setAttribute('vector-effect', 'non-scaling-stroke');
      if (cls) l.setAttribute('class', cls);
      svg.append(l);
    };
    line(0, 17, 400, 17, 'base');
    for (let i = 0; i < n; i++) {
      const x = n === 1 ? 210 : ((i + 0.5 + (rnd() - 0.5) * 0.8) / n) * 400;
      line(x.toFixed(1), 2, x.toFixed(1), 17);
    }
  });

  // ---------- Chapter model ----------

  // The HTML is timed in "script time". When narration.js is present, each
  // chapter is stretched to fit its voice: scripted times map through the
  // chapter's anchors, piecewise-linearly, so visuals land on the words.
  const NARRATION = window.ORIVEDA_NARRATION || null;
  const warpFor = (id) => {
    const a = NARRATION && NARRATION.chapters[id] ? NARRATION.chapters[id].anchors : null;
    if (!a) return (x) => x;
    return (x) => {
      if (x === Infinity) return x;
      for (let k = 1; k < a.length; k++) {
        if (x <= a[k][0]) {
          const [x0, y0] = a[k - 1];
          const [x1, y1] = a[k];
          return x1 === x0 ? y1 : y0 + ((x - x0) * (y1 - y0)) / (x1 - x0);
        }
      }
      const [xl, yl] = a[a.length - 1];
      return yl + (x - xl);
    };
  };

  let total = 0;
  const chapters = [...document.querySelectorAll('#plate > .scene')].map((el, i) => {
    const W = warpFor(el.id);
    // Entrances keep their speed; only long sweeps stretch with the chapter.
    const dur = (node, at) => {
      if (reduceMotion) return 0.001;
      const d = parseFloat(node.dataset.dur) || 0.7;
      return d > 1.5 ? W(at + d) - W(at) : d;
    };
    const timed = [...el.querySelectorAll('[data-at]')]
      .filter((node) => !node.closest('.caps'))
      .map((node) => {
        const mark = node.dataset.mark || null;
        const at = parseFloat(node.dataset.at);
        return {
          node,
          at: W(at),
          out: node.dataset.out ? W(parseFloat(node.dataset.out)) : Infinity,
          dur: dur(node, at),
          ease: EASES[node.dataset.ease] || EASES.out,
          read: node.dataset.read || '',
          mark,
          target: mark ? (node.dataset.target ? el.querySelector(node.dataset.target) : el) : null,
          draw: node.classList.contains('draw'),
          words: node.classList.contains('mask') ? [...node.querySelectorAll('.wi')].map((w) => ({ w, last: -1 })) : null,
          type: node.hasAttribute('data-type') ? { cps: parseFloat(node.dataset.type) || 30, full: node.textContent, shown: -1 } : null,
          last: -1,
        };
      });
    const spoken = NARRATION && NARRATION.chapters[el.id] ? NARRATION.chapters[el.id].lines : [];
    const caps = [...el.querySelectorAll('.caps .cap')].map((node, k) => ({
      at: W(parseFloat(node.dataset.at)),
      out: node.dataset.out ? W(parseFloat(node.dataset.out)) : Infinity,
      text: node.textContent.trim(),
      len: spoken[k] || null,
    }));
    const d = NARRATION && NARRATION.chapters[el.id] ? NARRATION.chapters[el.id].dur : parseFloat(el.dataset.duration) || 10;
    const ch = { el, i, id: el.id, title: el.dataset.title, start: total, dur: d, timed, caps, body: el.querySelector('.plate-body') };
    total += d;
    return ch;
  });

  // Writes one chapter's frame at local time `local`. Returns the last element
  // that just started to appear, so the camera can follow it.
  const setScene = (ch, local, readMode) => {
    let revealed = null;
    for (const e of ch.timed) {
      let p;
      if (readMode) p = e.read ? 0 : 1;
      else {
        const pin = e.ease(clamp01((local - e.at) / e.dur));
        const pout = e.out === Infinity ? 1 : 1 - clamp01((local - e.out) / (reduceMotion ? 0.001 : 0.3));
        p = Math.min(pin, pout);
      }

      if (e.words) {
        e.words.forEach((wd, i) => {
          const wp = readMode ? 1 : e.ease(clamp01((local - e.at - i * 0.07) / (reduceMotion ? 0.001 : 0.8)));
          if (Math.abs(wp - wd.last) < 0.0005) return;
          wd.last = wp;
          wd.w.style.transform = `translateY(${((1 - wp) * 110).toFixed(2)}%)`;
        });
      }
      if (e.type) {
        const ty = e.type;
        const n = readMode ? ty.full.length : Math.max(0, Math.min(ty.full.length, Math.floor((local - e.at) * ty.cps)));
        if (n !== ty.shown) {
          ty.shown = n;
          e.node.textContent = ty.full.slice(0, n);
        }
        e.node.classList.toggle('typing', !readMode && local >= e.at && n < ty.full.length);
      }

      if (Math.abs(p - e.last) < 0.0005) continue;
      if (e.last <= 0 && p > 0 && !e.mark) revealed = e.node;
      e.last = p;
      const v = p.toFixed(4);
      if (e.mark) e.target.style.setProperty(`--${e.mark}`, v);
      else e.node.style.setProperty('--p', v);
      if (e.draw) e.node.style.strokeDashoffset = (1 - p).toFixed(4);
    }
    return revealed;
  };

  // On small screens a plate can be taller than the stage: scroll so whatever
  // just appeared is in view, like a camera.
  const follow = (scroller, node) => {
    if (!scroller || scroller.scrollHeight <= scroller.clientHeight) return;
    const s = scroller.getBoundingClientRect();
    const r = node.getBoundingClientRect();
    const bottom = s.bottom - 20;
    if (r.bottom <= bottom) return;
    const delta = r.height > bottom - s.top - 16 ? r.top - s.top - 16 : r.bottom - bottom;
    scroller.scrollBy({ top: delta, behavior: reduceMotion ? 'auto' : 'smooth' });
  };

  // ---------- Player state ----------

  let t = 0;
  let playing = false;
  let ended = false;
  let rate = 1;
  let current = -1;
  let dirty = true;
  let dragging = false;
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
  const num = (i) => String(i + 1).padStart(2, '0');

  // ---------- Build navigation ----------

  const timeline = $('#timeline');
  const tip = $('#tip');
  const menu = $('#chapter-menu');
  const keys = $('#keys');
  const indexList = $('#index-list');
  const indexTrack = indexList.parentElement;
  const indexFill = $('#index-fill');
  const subtitle = $('#subtitle');
  const timeEl = $('#time');
  const nowTitle = $('#now-title');
  const btnPlay = $('#btn-play');

  for (const ch of chapters) {
    const seg = document.createElement('div');
    seg.className = 'seg';
    seg.style.flex = `${ch.dur} 1 0`;
    seg.innerHTML = '<span class="seg-fill"></span>';
    timeline.insertBefore(seg, tip);
    ch.seg = seg;
    ch.fill = seg.firstChild;

    const li = document.createElement('li');
    const a = document.createElement('a');
    a.href = `#${ch.id}`;
    a.innerHTML = `<span class="n">${num(ch.i)}</span><span class="t"></span><span class="d">${fmt(ch.start)}</span>`;
    a.querySelector('.t').textContent = ch.title;
    a.addEventListener('click', (e) => {
      if (readMode) return;
      e.preventDefault();
      goChapter(ch.i);
    });
    li.append(a);
    indexList.append(li);
    ch.indexItem = li;
    ch.indexLink = a;

    const mli = document.createElement('li');
    mli.innerHTML = `<button type="button"><span class="n">${num(ch.i)}</span><span></span><span class="d">${fmt(ch.start)}</span></button>`;
    mli.querySelector('span:nth-child(2)').textContent = ch.title;
    mli.firstChild.addEventListener('click', () => { goChapter(ch.i); closePopovers(); });
    menu.append(mli);
    ch.menuItem = mli.firstChild;
  }
  timeline.setAttribute('aria-valuemax', String(Math.round(total)));

  // The index rail fills to the current chapter, and through it by `frac`.
  const setRail = (idx, frac) => {
    const li = chapters[idx].indexItem;
    const h = indexTrack.offsetHeight;
    if (!h) return;
    indexFill.style.transform = `scaleY(${((li.offsetTop + frac * li.offsetHeight) / h).toFixed(4)})`;
  };

  // Writing the hash before the page has loaded makes the browser jump to it
  // on load, so wait until then.
  let loaded = document.readyState === 'complete';
  const syncHash = () => {
    if (loaded && current >= 0) history.replaceState(null, '', `${location.pathname}${location.search}#${chapters[current].id}`);
  };
  addEventListener('load', () => { loaded = true; syncHash(); });

  const setCurrent = (idx) => {
    if (idx === current) return;
    const prev = chapters[current];
    current = idx;
    const ch = chapters[idx];
    if (!readMode) {
      if (prev) prev.el.classList.remove('active');
      ch.el.classList.add('active');
      if (ch.body) ch.body.scrollTop = 0;
    }
    for (const c of chapters) {
      const cur = String(c === ch);
      c.seg.classList.toggle('active', c === ch);
      c.indexLink.setAttribute('aria-current', cur);
      c.menuItem.setAttribute('aria-current', cur);
    }
    nowTitle.textContent = `${num(idx)} / ${num(chapters.length - 1)} · ${ch.title}`;
    syncHash();
  };

  // Subtitles light up word by word: in step with the voice when there is
  // narration (by character position within the spoken line), otherwise at a
  // reading pace.
  let subCap = null;
  let subWords = [];
  let subMarks = [];
  const renderSubtitle = (ch, local) => {
    const cap = ch.caps.find((c) => local >= c.at && local < c.out) || null;
    if (cap !== subCap) {
      subCap = cap;
      subtitle.textContent = '';
      subWords = [];
      subMarks = [];
      if (cap) {
        const p = document.createElement('p');
        const words = cap.text.split(/\s+/);
        const chars = words.reduce((n, w) => n + w.length + 1, 0);
        let seen = 0;
        words.forEach((w, i) => {
          if (i) p.append(' ');
          const s = document.createElement('span');
          s.textContent = w;
          p.append(s);
          subWords.push(s);
          subMarks.push(cap.len ? cap.at + (seen / chars) * cap.len : cap.at + 0.1 + (i / words.length) * Math.max(0.8, (Math.min(cap.out, ch.dur) - cap.at) * 0.62));
          seen += w.length + 1;
        });
        subtitle.append(p);
      }
    }
    if (!cap) return;
    subWords.forEach((s, i) => s.classList.toggle('lit', local >= subMarks[i]));
  };

  const render = () => {
    dirty = false;
    const idx = chapterAt(t);
    setCurrent(idx);
    const ch = chapters[idx];
    const local = t - ch.start;
    // On the cover, the plate is shown fully drawn while the clock waits at t.
    const shown = onCover ? Math.max(local, ch.dur - 0.2) : local;
    ch.el.style.setProperty('--sp', reduceMotion ? '1' : clamp01(shown / 0.35).toFixed(3));
    const revealed = setScene(ch, shown, false);
    if (revealed && !dragging && !onCover) follow(ch.body, revealed);
    renderSubtitle(ch, local);
    for (const c of chapters) c.fill.style.width = `${(clamp01((t - c.start) / c.dur) * 100).toFixed(2)}%`;
    setRail(idx, clamp01(local / ch.dur));
    timeEl.textContent = `${fmt(t)} / ${fmt(total)}`;
    timeline.setAttribute('aria-valuenow', String(Math.round(t)));
    timeline.setAttribute('aria-valuetext', `${fmt(t)}, ${ch.title}`);
  };

  // ---------- Narration ----------

  // One audio track for the whole film. While it plays, it is the clock:
  // the frame follows voice.currentTime, so a stalled download holds the
  // picture instead of letting it run ahead of the words.
  const voice = NARRATION ? new Audio(NARRATION.src) : null;
  if (voice) voice.preload = 'auto';
  let soundOn = false;
  let ccChosen = false;
  const btnSound = $('#btn-sound');
  // Trust the voice's position only once it has settled near ours: while it
  // seeks or buffers, or on a server that can't seek, the picture keeps time.
  const voiceIsClock = () =>
    soundOn && voice && !voice.paused && !voice.seeking && voice.readyState >= 2 && Math.abs(voice.currentTime - t) < 0.5;

  function syncVoice() {
    if (!voice) return;
    if (!(soundOn && playing && !readMode && !dragging)) {
      if (!voice.paused) voice.pause();
      return;
    }
    voice.playbackRate = rate;
    if (Math.abs(voice.currentTime - t) > 0.15) voice.currentTime = t;
    if (voice.paused) voice.play().catch(() => setSound(false));
  }

  function setSound(on) {
    soundOn = !!(on && voice);
    btnSound.setAttribute('aria-pressed', String(soundOn));
    btnSound.setAttribute('aria-label', soundOn ? 'Mute narration' : 'Play narration');
    // Voice and subtitles together are a lot to take in, so subtitles follow
    // the sound until the viewer picks for themselves.
    if (!ccChosen) setCaptions(!soundOn);
    syncVoice();
  }

  // ---------- Clock ----------

  // The loop only runs while playing or while a frame is pending; a paused
  // player costs nothing.
  let rafId = 0;
  let last = null;
  let lastSync = 0;
  const kick = () => { if (!rafId) rafId = requestAnimationFrame(frame); };
  const invalidate = () => { dirty = true; kick(); };
  function frame(now) {
    rafId = 0;
    if (playing && !readMode) {
      if (voiceIsClock()) t = Math.min(voice.currentTime, total);
      else {
        if (last !== null) t += Math.min(0.1, (now - last) / 1000) * rate;
        // Pull a drifted voice back to the picture, at most once a second.
        if (soundOn && voice && !voice.seeking && now - lastSync > 1000) {
          lastSync = now;
          syncVoice();
        }
      }
      last = now;
      if (t >= total - 0.02) {
        t = total;
        ended = true;
        setPlaying(false);
      }
      dirty = true;
    }
    if (dirty && !readMode) render();
    if (playing && !readMode) kick();
  }

  const setPlaying = (p) => {
    playing = p;
    last = null;
    root.classList.toggle('paused', !p);
    root.classList.toggle('ended', ended && !p);
    btnPlay.setAttribute('aria-label', p ? 'Pause' : ended ? 'Replay' : 'Play');
    if (p) kick();
    syncVoice();
  };

  const seek = (time) => {
    const leaving = chapters[current];
    t = Math.min(Math.max(0, time), total);
    // The chapter we leave goes back to its first frame, so coming back to it
    // replays it rather than showing it frozen mid-way.
    if (leaving && leaving.i !== chapterAt(t)) setScene(leaving, -1, false);
    if (ended && t < total) { ended = false; setPlaying(playing); }
    if (!dragging) syncVoice();
    invalidate();
  };

  // Before the first play the stage shows a cover: the opening plate fully
  // drawn, with a choice to play with or without narration. Starting from a
  // click is also what lets the browser play sound.
  let onCover = false;
  const begin = (withSound) => {
    onCover = false;
    root.classList.remove('cover');
    setSound(withSound);
  };

  const goChapter = (i) => {
    i = Math.max(0, Math.min(chapters.length - 1, i));
    if (readMode) {
      chapters[i].el.scrollIntoView({ behavior: reduceMotion ? 'auto' : 'smooth' });
      return;
    }
    if (onCover) begin(true);
    seek(chapters[i].start);
    if (!playing) setPlaying(true);
  };

  const togglePlay = () => {
    if (onCover) { begin(true); seek(t); setPlaying(true); }
    else if (ended) { ended = false; seek(0); setPlaying(true); }
    else setPlaying(!playing);
  };

  const prevChapter = () => goChapter(t - chapters[current].start > 2 ? current : current - 1);
  const nextChapter = () => { if (current < chapters.length - 1) goChapter(current + 1); };

  // ---------- Timeline scrubbing ----------

  const timeFromX = (x) => {
    for (const ch of chapters) {
      const r = ch.seg.getBoundingClientRect();
      if (x <= r.right + 1.5 || ch === chapters[chapters.length - 1]) {
        return ch.start + clamp01((x - r.left) / r.width) * ch.dur;
      }
    }
    return 0;
  };

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
    tip.style.left = `${Math.min(box.width - 80, Math.max(80, e.clientX - box.left))}px`;
    if (dragging) seek(time);
  });
  const endDrag = () => {
    if (!dragging) return;
    dragging = false;
    timeline.classList.remove('dragging');
    syncVoice();
  };
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
  function setCaptions(on) {
    root.classList.toggle('no-cc', !on);
    btnCc.setAttribute('aria-pressed', String(on));
  }
  const toggleCaptions = () => {
    ccChosen = true;
    setCaptions(root.classList.contains('no-cc'));
  };
  btnCc.addEventListener('click', toggleCaptions);

  const toggleSound = () => {
    if (onCover) togglePlay();
    else setSound(!soundOn);
  };
  if (voice) btnSound.addEventListener('click', toggleSound);
  else btnSound.hidden = true;

  $('#cta-len').textContent = fmt(total);
  if (!voice) $('#cta-sound').firstChild.nextSibling.textContent = 'Play ';
  $('#cta-sound').addEventListener('click', togglePlay);
  $('#cta-muted').addEventListener('click', () => { begin(false); seek(t); setPlaying(true); });
  $('#cta-read').addEventListener('click', () => setMode(true));
  if (!voice) $('#cta-muted').hidden = true;

  const btnSpeed = $('#btn-speed');
  const cycleSpeed = () => {
    rate = RATES[(RATES.indexOf(rate) + 1) % RATES.length];
    btnSpeed.textContent = `${rate}×`;
    syncVoice();
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
  function closePopovers() {
    popovers.forEach(([b, p]) => { p.hidden = true; b.setAttribute('aria-expanded', 'false'); });
  }
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

  // Clicking the plate itself plays/pauses, like a video.
  $('#plate').addEventListener('click', (e) => {
    if (readMode || e.target.closest('a, button, pre, .term')) return;
    if (String(getSelection())) return;
    togglePlay();
  });

  document.querySelectorAll('[data-copy]').forEach((btn) => {
    btn.addEventListener('click', async () => {
      const src = document.querySelector(btn.dataset.copy);
      try {
        await navigator.clipboard.writeText(src.textContent);
        btn.textContent = 'Copied';
      } catch {
        const range = document.createRange();
        range.selectNodeContents(src);
        getSelection().removeAllRanges();
        getSelection().addRange(range);
        btn.textContent = 'Press Ctrl+C';
      }
      setTimeout(() => { btn.textContent = 'Copy'; }, 1800);
    });
  });

  // ---------- Watch / Read ----------

  const btnWatch = $('#mode-watch');
  const btnRead = $('#mode-read');

  // In Read mode the rail and header follow the plate in view.
  const readProgress = () => {
    if (!readMode) return;
    const line = innerHeight * 0.4;
    let idx = 0;
    chapters.forEach((c, i) => { if (c.el.getBoundingClientRect().top <= line) idx = i; });
    const r = chapters[idx].el.getBoundingClientRect();
    setCurrent(idx);
    setRail(idx, clamp01((line - r.top) / r.height));
  };
  let scrollQueued = false;
  addEventListener('scroll', () => {
    if (!readMode || scrollQueued) return;
    scrollQueued = true;
    requestAnimationFrame(() => { scrollQueued = false; readProgress(); });
  }, { passive: true });

  const setMode = (read) => {
    const idx = readMode ? Math.max(0, current) : chapterAt(t);
    readMode = read;
    root.classList.toggle('read', read);
    root.classList.toggle('watch', !read);
    btnWatch.setAttribute('aria-pressed', String(!read));
    btnRead.setAttribute('aria-pressed', String(read));
    const url = new URL(location.href);
    url.searchParams.delete('t');
    if (read) url.searchParams.set('read', ''); else url.searchParams.delete('read');
    history.replaceState(null, '', url.toString().replace('?read=', '?read'));
    closePopovers();

    if (read) {
      setPlaying(false);
      chapters.forEach((c) => { c.el.classList.remove('active'); setScene(c, Infinity, true); });
      setCurrent(idx);
      chapters[idx].el.scrollIntoView();
      readProgress();
    } else {
      chapters.forEach((c) => setScene(c, -1, false));
      window.scrollTo(0, 0);
      current = -1;
      subCap = null;
      showCover(chapters[idx].start);
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
    if ((k === ' ' || k === 'Enter') && e.target.closest('button, a')) return;

    if (k === ' ' || k === 'k' || k === 'K') togglePlay();
    else if (k === 'ArrowLeft') seek(t - 5);
    else if (k === 'ArrowRight') seek(t + 5);
    else if (k === 'Home') seek(0);
    else if (k === 'End') seek(total);
    else if (k === 'p' || k === 'P') prevChapter();
    else if (k === 'n' || k === 'N') nextChapter();
    else if (/^[1-9]$/.test(k) && +k <= chapters.length) goChapter(+k - 1);
    else if (k === 'c' || k === 'C') toggleCaptions();
    else if (k === 'm' || k === 'M') toggleSound();
    else if (k === 's' || k === 'S') cycleSpeed();
    else if (k === 'f' || k === 'F') toggleFullscreen();
    else if (k === '?') btnKeys.click();
    else return;
    e.preventDefault();
  });

  addEventListener('hashchange', () => {
    const i = chapters.findIndex((c) => `#${c.id}` === location.hash);
    if (i >= 0 && !readMode) goChapter(i);
  });
  addEventListener('resize', () => { if (readMode) readProgress(); else invalidate(); });

  // ---------- Start ----------

  function showCover(at) {
    setPlaying(false);
    seek(at);
    onCover = true;
    root.classList.add('cover');
    invalidate();
  }

  const startIdx = Math.max(0, chapters.findIndex((c) => `#${c.id}` === location.hash));
  // ?t=<seconds> starts at a timestamp, like a video link.
  const startT = parseFloat(new URLSearchParams(location.search).get('t'));
  if (readMode) {
    setPlaying(false);
    chapters.forEach((c) => setScene(c, Infinity, true));
    setCurrent(startIdx);
    if (location.hash) chapters[startIdx].el.scrollIntoView();
    readProgress();
  } else {
    chapters.forEach((c) => setScene(c, -1, false));
    showCover(Number.isFinite(startT) ? startT : chapters[startIdx].start);
  }
  // Fonts change line wrapping, and so the rail's geometry.
  document.fonts?.ready.then(() => { if (readMode) readProgress(); else invalidate(); });
})();
