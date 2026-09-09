/* A–D requirement illustrations; coordinates are explanatory, not robot plans. */
(function () {
  'use strict';
  const line = (a,b,seconds,phase,direction=1) => ({points:[a,[a[0]+(b[0]-a[0])/3,a[1]+(b[1]-a[1])/3],[a[0]+2*(b[0]-a[0])/3,a[1]+2*(b[1]-a[1])/3],b],seconds,phase,direction});
  const curve = (points,seconds,phase) => ({points,seconds,phase,direction:1});
  const insert = () => line([420,160],[483,160],2.8,'저속 삽입');
  const cases = {
    A:{segments:[line([85,160],[420,160],4.2,'직진 접근'),insert()]},
    B:{segments:[curve([[85,260],[205,260],[260,160],[420,160]],6,'곡선 정렬'),insert()]},
    C:{segments:[line([342,236],[108,236],3.7,'후진 · 공간 확보',-1),curve([[108,236],[215,236],[275,160],[420,160]],5,'재접근 · 정렬'),insert()]},
    D:{segments:[line([342,236],[280,236],2.4,'후방 확인 · 제한 후진',-1),curve([[280,236],[340,236],[360,160],[420,160]],5.4,'방향 정렬 · 재접근'),insert()]}
  };
  function pointAt(points,t) {
    const u=1-t, [a,b,c,d]=points;
    const xy=[0,1].map(k=>u*u*u*a[k]+3*u*u*t*b[k]+3*u*t*t*c[k]+t*t*t*d[k]);
    const tangent=[0,1].map(k=>3*u*u*(b[k]-a[k])+6*u*t*(c[k]-b[k])+3*t*t*(d[k]-c[k]));
    return {x:xy[0],y:xy[1],angle:Math.atan2(tangent[1],tangent[0])*180/Math.PI};
  }
  // Arc-length lookup keeps the vehicle moving continuously through curved paths.
  for (const value of Object.values(cases)) {
    value.duration=0.9;
    value.segments.forEach(s=>{
      s.lengths=[0]; let p=pointAt(s.points,0);
      for(let i=1;i<=160;i++) {const n=pointAt(s.points,i/160);s.lengths.push(s.lengths.at(-1)+Math.hypot(n.x-p.x,n.y-p.y));p=n;}
      value.duration+=s.seconds;
    });
  }
  function fractionAt(s,f) {
    const target=f*s.lengths.at(-1);
    let i=1;while(i<160 && s.lengths[i]<target)i++;
    return (i-1+(target-s.lengths[i-1])/(s.lengths[i]-s.lengths[i-1]))/160;
  }
  function sample(id,seconds) {
    const value=cases[id]; let remaining=Math.max(0,seconds-0.9),index=0;
    while(index<value.segments.length-1 && remaining>value.segments[index].seconds) remaining-=value.segments[index++].seconds;
    const s=value.segments[index], f=seconds>=value.duration?1:Math.min(1,remaining/s.seconds),p=pointAt(s.points,fractionAt(s,f));
    p.angle=(p.angle+(s.direction<0?180:0)+360)%360;
    if(p.angle>180)p.angle-=360;
    return {...p,index,f,direction:s.direction,phase:seconds<0.9?'팔레트 인식':seconds>=value.duration?'삽입 완료':s.phase};
  }
  if(typeof module!=='undefined' && module.exports) module.exports={cases,sample};
  if(typeof document==='undefined')return;

  const reduced=window.matchMedia('(prefers-reduced-motion: reduce)');
  let active=null, scenes=[],elapsed=0,last=null,frame=0,paused=reduced.matches;
  function renderScene(scene,seconds) {
    const id=scene.dataset.motionCase,p=sample(id,seconds);
    scene.querySelector('.motion-vehicle').setAttribute('transform',`translate(${p.x.toFixed(3)} ${p.y.toFixed(3)}) rotate(${p.angle.toFixed(3)})`);
    const label=scene.querySelector('.motion-phase');
    if(label.textContent!==p.phase)label.textContent=p.phase;
    const direction=p.direction<0?'reverse':'forward';
    if(scene.dataset.direction!==direction)scene.dataset.direction=direction;
    scene.querySelectorAll('.motion-trace').forEach((path,i)=>path.setAttribute('stroke-dasharray',`${i<p.index?1:i===p.index?p.f:0} 1`));
    scene.querySelector('.motion-progress').style.transform=`scaleX(${Math.min(1,seconds/cases[id].duration)})`;
  }
  function prepare(scene) {
    if(scene.dataset.motionReady)return;
    scene.dataset.motionReady='true';
    const ns='http://www.w3.org/2000/svg', group=scene.querySelector('.motion-paths');
    cases[scene.dataset.motionCase].segments.forEach(s=>{
      const [a,b,c,d]=s.points, data=`M ${a} C ${b} ${c} ${d}`;
      for(const kind of ['motion-plan','motion-trace']) {
        const path=document.createElementNS(ns,'path');
        path.setAttribute('d',data);path.setAttribute('class',kind+(s.direction<0?' motion-reverse':''));path.setAttribute('pathLength','1');
        if(kind==='motion-trace')path.setAttribute('stroke-dasharray','0 1');
        group.appendChild(path);
      }
    });
  }
  function buttons() {
    if(!active)return;
    const b=active.querySelector('[data-motion-toggle]');
    if(b) {b.textContent=paused?'재생':'일시정지';b.setAttribute('aria-label',paused?'접근 시나리오 재생':'접근 시나리오 일시정지');}
  }
  function render(){scenes.forEach(s=>renderScene(s,elapsed));buttons();}
  function tick(now) {
    frame=0;
    if(paused || document.hidden || !scenes.length)return;
    if(last!==null)elapsed+=(now-last)/1000;
    last=now;
    const end=Math.max(...scenes.map(s=>cases[s.dataset.motionCase].duration));
    if(elapsed>end+2.2)elapsed=0;
    render();frame=requestAnimationFrame(tick);
  }
  function run(){cancelAnimationFrame(frame);last=null;if(!paused&&!document.hidden&&scenes.length)frame=requestAnimationFrame(tick);}
  function activate(slide) {
    if(slide===active)return;
    cancelAnimationFrame(frame);active=slide;scenes=slide?Array.from(slide.querySelectorAll('[data-motion-case]')):[];
    scenes.forEach(prepare);elapsed=0;paused=reduced.matches;render();run();
  }
  document.addEventListener('slidechange',e=>activate(e.detail.slide));
  // Delegation works after the UOS runtime mounts and across its shadow boundary.
  document.addEventListener('click',e=>{
    const button=e.composedPath().find(n=>n instanceof Element && n.matches('[data-motion-toggle],[data-motion-replay]'));
    if(!button||!active||!active.contains(button))return;
    if(button.hasAttribute('data-motion-replay')){elapsed=0;paused=false;}else paused=!paused;
    render();run();
  });
  document.addEventListener('keydown',e=>{
    if((e.key===' '||e.key==='Enter') && e.composedPath().some(n=>n instanceof Element && n.matches('[data-motion-toggle],[data-motion-replay]')))e.stopPropagation();
  });
  document.addEventListener('visibilitychange',run);
  reduced.addEventListener('change',()=>{paused=reduced.matches;render();run();});
  window.addEventListener('beforeprint',()=>{cancelAnimationFrame(frame);scenes.forEach(s=>renderScene(s,cases[s.dataset.motionCase].duration));});
  window.addEventListener('afterprint',()=>{render();run();});
  // Handles a cached runtime that mounted before this script was evaluated.
  const current=document.querySelector('deck-stage > [data-deck-active]');
  if(current)activate(current);
}());
