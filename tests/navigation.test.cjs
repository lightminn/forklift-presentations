const {test} = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

function navigate(file, href) {
  const html = fs.readFileSync(path.join(__dirname, '..', file), 'utf8');
  let destination = null;
  const url = new URL(href);
  const location = {href, hash: url.hash, search: url.search,
    replace(value) { destination = String(value); }};
  for (const match of html.matchAll(/<script>([\s\S]*?)<\/script>/g)) {
    vm.runInNewContext(match[1], {location, URL});
  }
  return destination;
}

test('archive stays at the root unless an original slide number is provided', () => {
  const base = 'https://example.github.io/forklift-presentations/';
  assert.equal(navigate('index.html', base), null);
  assert.equal(navigate('index.html', base + '#weeks'), null);
  assert.equal(navigate('index.html', base + '#14'), null);
  assert.equal(navigate('index.html', base + '?v=old#10'), base + 'week-02/?v=old#10');
  assert.equal(navigate('index.html', base + 'index.html#7'), base + 'week-02/#7');
});

test('latest redirects under the repository prefix while preserving slide and query', () => {
  const root = path.join(__dirname, '..');
  const published = fs.readdirSync(root).filter(name => /^week-\d+$/.test(name))
    .map(name => JSON.parse(fs.readFileSync(path.join(root, name, 'week.json'), 'utf8')))
    .filter(week => week.status === 'published');
  const latest = String(Math.max(...published.map(week => week.week))).padStart(2, '0');
  assert.equal(navigate('latest/index.html',
    'https://example.github.io/forklift-presentations/latest/?view=full#8'),
    `https://example.github.io/forklift-presentations/week-${latest}/?view=full#8`);
});
