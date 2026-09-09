const {test} = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const source = path.join(__dirname, '../case-motion.js');
const crypto = require('node:crypto');

test('animations retain original forklift and pallet photography and both D alternatives', () => {
  const html=fs.readFileSync(path.join(__dirname,'../index.html'),'utf8');
  assert.ok(html.includes('assets/forklift-original.png'),'Use original forklift image');
  assert.ok(html.includes('assets/pallet-original.png'),'Use original pallet image');
  assert.ok(html.includes('data-motion-case="D1"'),'Keep rotation alternative');
  assert.ok(html.includes('data-motion-case="D2"'),'Keep limited reverse alternative');
  assert.equal((html.match(/data-obstacle="left"/g)||[]).length,2,'Both alternatives need the original left obstacle');
  assert.equal((html.match(/data-obstacle="rear"/g)||[]).length,2,'Both alternatives need the original rear obstacle');
  assert.ok(!html.includes('motion-chassis'),'Do not replace photographs with a drawn vehicle');
});

const reference=require('../assets/approach-source.json');
const {cases,sample}=require(source);
const close=(a,b,tol=1e-7)=>Math.abs(a-b)<tol;
const angleDelta=(a,b)=>((a-b+540)%360)-180;

test('image bytes are exactly the original Google Slides embedded assets',()=>{
  const expected={
    'forklift-original.png':'2c13a08c6ffaddbfb60661c7ccffba6f2c61b2904694356acc304725a36f165c',
    'pallet-original.png':'ae8bc34eb480536ba54137d8c964a99ff628981ae0b69f6f03e1e33040e2aa33'
  };
  for(const [name,hash] of Object.entries(expected))assert.equal(crypto.createHash('sha256').update(fs.readFileSync(path.join(__dirname,'../assets',name))).digest('hex'),hash,name);
});

test('every source start, intermediate and insertion pose is retained',()=>{
  for(const [id,ref] of Object.entries(reference.scenes)) {
    const checkpoints=[0];let t=.9;
    for(const seg of cases[id].segments){t+=seg.seconds;checkpoints.push(t);}
    for(const [label,pose] of Object.entries(ref.poses)) {
      assert.ok(checkpoints.some(t=>{const p=sample(id,t);return close(p.x,pose[0])&&close(p.y,pose[1])&&Math.abs(angleDelta(p.angle,pose[2]))<.001;}),`${id} ${label} must match the source element`);
    }
    assert.equal(sample(id,cases[id].duration).phase,'삽입 완료');
  }
});

test('C backs farther than D2 and both D alternatives preserve obstacle clearance',()=>{
  const retreat=id=>Math.max(...Array.from({length:1201},(_,i)=>sample(id,cases[id].duration*i/1200).y))-reference.scenes[id].poses.start[1];
  assert.ok(retreat('C')>100);
  assert.ok(retreat('D2')>25&&retreat('D2')<35);
  for(const id of ['D1','D2'])for(let i=0;i<=1400;i++) {
    const p=sample(id,cases[id].duration*i/1400),a=(p.angle+180)*Math.PI/180;
    // Source photograph's full cropped image rectangle, including both forks.
    const w=reference.vehicle.width/2,h=reference.vehicle.height/2;
    const pts=[[-w,-h],[-w,h],[w,h],[w,-h]].map(([x,y])=>[p.x+x*Math.cos(a)-y*Math.sin(a),p.y+x*Math.sin(a)+y*Math.cos(a)]);
    for(const [x,y,w,h] of reference.scenes[id].obstacles) {
      const minX=Math.min(...pts.map(p=>p[0])),maxX=Math.max(...pts.map(p=>p[0])),minY=Math.min(...pts.map(p=>p[1])),maxY=Math.max(...pts.map(p=>p[1]));
      assert.ok(maxX<x||minX>x+w||maxY<y||minY>y+h,`${id} obstacle clearance at ${i}`);
    }
  }
});

test('source poses are connected continuously and rotation is confined to D1',()=>{
  for(const id of Object.keys(cases)) {
    let prev=sample(id,0);
    for(let i=1;i<=4000;i++) {
      const p=sample(id,cases[id].duration*i/4000);
      const dx=p.x-prev.x,dy=p.y-prev.y,d=Math.hypot(dx,dy);
      assert.ok(d<2,`${id}: position discontinuity`);
      assert.ok(Math.abs(angleDelta(p.angle,prev.angle))<2,`${id}: heading discontinuity`);
      if(d>.001) {
        const heading=(prev.angle+angleDelta(p.angle,prev.angle)/2)*Math.PI/180;
        assert.ok(Math.abs(-dx*Math.sin(heading)+dy*Math.cos(heading))<.035,`${id}: sideways translation`);
      }else if(id!=='D1')assert.ok(Math.abs(angleDelta(p.angle,prev.angle))<.1,`${id}: unexpected stationary rotation`);
      prev=p;
    }
  }
});
