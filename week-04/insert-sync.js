/* Drive the insertion concept diagram from the clip beside it.
 *
 * The diagram (svg[data-sync]) and the camera clip sit on the same slide. The
 * deck restarts the clip from 0 whenever the slide becomes active and loops
 * it, so reading video.currentTime every frame keeps both in step on every
 * loop. data-sync holds four clip times in seconds: pocket estimate shown,
 * approach starts, insertion starts, insertion ends. Without this script the
 * CSS keyframes in deck.css still animate the diagram on their own clock.
 */
(function () {
  'use strict';
  const APPROACH_PX = 314;  // fork tip reaches the pallet face
  const INSERT_PX = 410;    // fork tip at the target depth

  function stageOf(t, [, tA, tI]) {
    if (t < tA) return 1;
    if (t < tI) return 2;
    return 3;
  }

  function offsetAt(t, [, tA, tI, tE]) {
    if (t < tA) return 0;
    if (t < tI) return APPROACH_PX * (t - tA) / (tI - tA);
    if (t < tE) return APPROACH_PX + (INSERT_PX - APPROACH_PX) * (t - tI) / (tE - tI);
    return INSERT_PX;
  }

  function update() {
    document.querySelectorAll('svg[data-sync]').forEach((svg) => {
      const slide = svg.closest('section');
      const video = slide && slide.querySelector('video');
      if (!video) return;
      slide.classList.add('ins-synced');
      const times = svg.dataset.sync.split(',').map(Number);
      const t = video.currentTime || 0;
      const x = offsetAt(t, times).toFixed(1);
      svg.querySelectorAll('.ins-move').forEach((g) => { g.style.transform = `translateX(${x}px)`; });
      svg.querySelectorAll('.ins-cone').forEach((c) => { c.style.opacity = t < times[1] ? '0.2' : '0'; });
      svg.querySelectorAll('.ins-est').forEach((e) => { e.style.opacity = t >= times[0] ? '1' : '0'; });
      const stage = stageOf(t, times);
      [1, 2, 3].forEach((n) => {
        slide.querySelectorAll(`.ins-s${n}`).forEach((s) => { s.style.opacity = n === stage ? '1' : '0.3'; });
      });
    });
    window.requestAnimationFrame(update);
  }

  if (typeof window !== 'undefined' && window.requestAnimationFrame) {
    window.requestAnimationFrame(update);
  }
  if (typeof module !== 'undefined' && module.exports) module.exports = { stageOf, offsetAt };
})();
