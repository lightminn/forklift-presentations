const {test} = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const source = path.join(__dirname, '../case-motion.js');

test('A-D replace static photos with playable motion scenes', () => {
  const html = fs.readFileSync(path.join(__dirname, '../index.html'), 'utf8');
  for (const id of ['A','B','C','D']) {
    assert.ok(html.includes(`data-motion-case="${id}"`),`Missing animated case ${id}`);
    assert.ok(!html.includes(`src="assets/case-${id.toLowerCase()}.png"`));
  }
});

test('A-D align both forks with the pallet and end at the insertion pose', () => {
  assert.ok(fs.existsSync(source), 'Motion model must exist');
  const {cases, sample} = require(source);
  for (const id of ['A','B','C','D']) {
    const end = sample(id, cases[id].duration);
    assert.equal(end.x,483,id);
    assert.equal(end.y,160,id);
    assert.equal(end.angle,0,id);
    assert.equal(end.phase,'삽입 완료',id);
  }
});

test('C retreats farther than D; D stays clear of its rear obstacle', () => {
  assert.ok(fs.existsSync(source), 'Motion model must exist');
  const {cases, sample} = require(source);
  const minX = id => Math.min(...Array.from({length:801},(_,i)=>sample(id,cases[id].duration*i/800).x));
  assert.ok(minX('C') < 150);
  assert.ok(minX('D') > 260);
  for (let i=0;i<=1000;i++) {
    const p=sample('D',cases.D.duration*i/1000);
    // Conservative body/wheel envelope in world coordinates.
    const a=p.angle*Math.PI/180;
    const points=[[-36,-32],[-36,32],[30,32],[30,-32]].map(([x,y])=>[p.x+x*Math.cos(a)-y*Math.sin(a),p.y+x*Math.sin(a)+y*Math.cos(a)]);
    assert.ok(Math.min(...points.map(p=>p[0])) > 238 || Math.max(...points.map(p=>p[1])) < 215,`D obstacle clearance at ${i}`);
  }
});

test('motion is continuous with no rotation in place or sideways translation', () => {
  assert.ok(fs.existsSync(source), 'Motion model must exist');
  const {cases,sample}=require(source);
  for (const id of ['A','B','C','D']) {
    let prev=sample(id,0);
    for(let i=1;i<=4000;i++) {
      const p=sample(id,cases[id].duration*i/4000);
      const dx=p.x-prev.x,dy=p.y-prev.y,d=Math.hypot(dx,dy);
      assert.ok(d<3,`${id}: discontinuity`);
      if(d>0.001) {
        const heading=(prev.angle+p.angle)/2*Math.PI/180;
        assert.ok(Math.abs(-dx*Math.sin(heading)+dy*Math.cos(heading))<0.035,`${id}: sideways drift`);
      } else assert.ok(Math.abs(p.angle-prev.angle)<0.1,`${id}: in-place rotation`);
      prev=p;
    }
  }
});
