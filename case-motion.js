/* Animate the separate image elements and poses from the original Google Slides. */
(function () {
  'use strict';
  const line = (a,b,seconds,phase,direction=1) => ({points:[a,[a[0]+(b[0]-a[0])/3,a[1]+(b[1]-a[1])/3],[a[0]+2*(b[0]-a[0])/3,a[1]+2*(b[1]-a[1])/3],b],seconds,phase,direction});
  const reference=typeof module!=='undefined' && module.exports?require('./assets/approach-source.json'):JSON.parse(document.getElementById('approach-reference').textContent);
  const curve = (points,seconds,phase,direction=1) => ({points,seconds,phase,direction});
  const turn = (point,from,to,seconds,phase) => ({points:[point,point,point,point],angles:[from,to],seconds,phase,direction:0});
  const xy=p=>p.slice(0,2);
  const offset=(p,angle,distance)=>[p[0]+Math.cos(angle*Math.PI/180)*distance,p[1]+Math.sin(angle*Math.PI/180)*distance];
  const cases={};
  for(const [id,ref] of Object.entries(reference.scenes)) {
    const s=xy(ref.poses.start),e=xy(ref.poses.end),v=ref.poses.via&&xy(ref.poses.via);
    const pre=[e[0],e[1]+(id==='C'?48:id.startsWith('D')?30:35)];
    let segments;
    if(id==='A') segments=[{...curve([s,[s[0],s[1]-18],[pre[0],pre[1]+18],pre],3,'직진 접근'),orientation:-90}];
    if(id==='B') {
      const angle=ref.poses.via[2];
      segments=[curve([s,offset(s,-90,22),offset(v,angle,-22),v],3.5,'곡선 접근'),curve([v,offset(v,angle,18),offset(pre,-90,-18),pre],2.3,'전면 정렬')];
    }
    if(id==='C') segments=[curve([s,[s[0],s[1]+48],[v[0],v[1]-40],v],3.6,'후진 · 공간 확보',-1),curve([v,[v[0],v[1]-35],[pre[0],pre[1]+35],pre],4,'재접근 · 정렬')];
    if(id==='D2') segments=[curve([s,[s[0],s[1]+15],[v[0],v[1]-15],v],3,'제한 거리 후진',-1),curve([v,[v[0],v[1]-18],[pre[0],pre[1]+18],pre],2.5,'전면 정렬')];
    if(id==='D1') {
      const heading=Math.atan2(v[1]-s[1],v[0]-s[0])*180/Math.PI;
      segments=[turn(s,-90,heading,1,'회전'),line(s,v,2,'위치 변경'),turn(v,heading,-180,.3,'위치 변경'),turn(v,-180,-180,.4,'위치 변경'),turn(v,-180,-90,.9,'전면 정렬'),curve([v,[v[0],v[1]-10],[pre[0],pre[1]+10],pre],1.6,'전면 정렬')];
    }
    segments.push(line(pre,e,2.3,'저속 삽입'));
    cases[id]={segments};
  }
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
    const s=value.segments[index], f=seconds>=value.duration?1:Math.min(1,remaining/s.seconds);
    const p=s.angles?{x:s.points[0][0],y:s.points[0][1],angle:s.angles[0]+(((s.angles[1]-s.angles[0]+540)%360)-180)*f}:pointAt(s.points,fractionAt(s,f));
    if(s.orientation!==undefined)p.angle=s.orientation;
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
    scene.querySelector('.motion-vehicle').setAttribute('transform',`translate(${p.x.toFixed(3)} ${p.y.toFixed(3)}) rotate(${(p.angle+180).toFixed(3)})`);
    const label=scene.querySelector('.motion-phase');
    if(label.textContent!==p.phase)label.textContent=p.phase;
    const direction=p.direction<0?'reverse':'forward';
    if(scene.dataset.direction!==direction)scene.dataset.direction=direction;
    scene.querySelector('.motion-progress').style.transform=`scaleX(${Math.min(1,seconds/cases[id].duration)})`;
  }
  function prepare(scene) {
    if(scene.dataset.motionReady)return;
    scene.dataset.motionReady='true';
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
