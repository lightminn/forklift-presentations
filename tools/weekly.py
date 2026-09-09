"""Shared catalog and HTML generation for weekly presentations (stdlib only)."""
from html import escape
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def week_number(value):
    number = int(value)
    if not 1 <= number <= 99:
        raise ValueError('week must be between 1 and 99')
    return number


def load_weeks(root):
    weeks = []
    for directory in sorted(root.glob('week-*')):
        try:
            if directory.is_symlink() or not directory.is_dir():
                raise ValueError('week must be a local directory')
            info = json.loads((directory / 'week.json').read_text(encoding='utf-8'))
            if type(info['week']) is not int:
                raise ValueError('week must be an integer')
            number = week_number(info['week'])
            if directory.name != f'week-{number:02d}':
                raise ValueError('directory name must match week')
            if info['status'] not in ('draft', 'published'):
                raise ValueError('status must be draft or published')
            if not isinstance(info['title'], str) or not info['title'].strip():
                raise ValueError('title must be a nonempty string')
            if not isinstance(info.get('summary', ''), str):
                raise ValueError('summary must be a string')
        except (OSError, ValueError, KeyError, TypeError) as error:
            raise SystemExit(f'{directory.name}/week.json: {error}') from error
        weeks.append({**info, 'directory': directory, 'path': directory.name + '/'})
    if not weeks:
        raise SystemExit('no weekly presentations found')
    return sorted(weeks, key=lambda week: week['week'], reverse=True)


def published_weeks(weeks):
    published = [week for week in weeks if week['status'] == 'published']
    if not published:
        raise SystemExit('at least one published week is required')
    return published


def archive_html(weeks):
    published = published_weeks(weeks)
    latest = published[0]
    rows = []
    for week in published:
        path, title = escape(week['path'], quote=True), escape(week['title'])
        summary = escape(week.get('summary', ''))
        label = '<span class="current">최근 발표</span>' if week is latest else ''
        rows.append(f'''<li data-week="{week['week']}"><a class="week-link" href="{path}">
<span class="week-number"><b>{week['week']:02d}</b><span>주차</span></span>
<div class="week-content"><div class="week-heading"><h3>{title}</h3>{label}</div><span class="summary">{summary}</span></div>
<span class="open-deck">발표자료 열기 <span aria-hidden="true">↗</span></span></a></li>''')
    legacy = next((week for week in published if week['week'] == 2), None)
    legacy_script = ''
    if legacy:
        count = len(json.loads((legacy['directory'] / 'slide-metadata.json').read_text(encoding='utf-8')))
        legacy_script = f'''<script>
const oldSlide = location.hash.match(/^#(\\d+)$/);
if (oldSlide && Number(oldSlide[1]) >= 1 && Number(oldSlide[1]) <= {count}) {{
  location.replace(new URL('week-02/' + location.search + location.hash, location.href));
}}
</script>'''
    fonts = escape(published[-1]['path'], quote=True) + 'vendor/uos-slide-template/fonts/fonts.css'
    return f'''<!DOCTYPE html>
<html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>자율 지게차 · 주차별 발표자료</title><meta name="description" content="임베디드구동 및 실습 자율 지게차 프로젝트의 주차별 발표자료">
<link rel="icon" href="data:,"><link rel="stylesheet" href="{fonts}"><link rel="stylesheet" href="archive.css">
{legacy_script}</head><body>
<header class="masthead"><span class="university">서울시립대학교</span><span>임베디드구동 및 실습</span></header>
<main>
<div class="intro"><p class="eyebrow">팔레트 핸들링 경로 생성 및 제어</p><h1>자율 지게차<br><span>주차별 발표자료</span></h1>
<p class="description">과제 분석부터 구현 및 검증까지, 주차별 개발 내용을 정리한다.</p>
<a class="latest-link" href="latest/">최근 발표 · {latest['week']}주차 <span aria-hidden="true">→</span></a></div>
<section class="archive" aria-labelledby="archive-title"><div class="section-heading"><h2 id="archive-title">발표 목록</h2><span>총 {len(published)}회</span></div>
<ol class="week-list">{''.join(rows)}</ol></section>
</main><footer><span>자율 지게차 프로젝트</span><a href="https://github.com/lightminn/forklift-presentations">원고 및 출처 · GitHub ↗</a></footer>
</body></html>
'''


def redirect_html(week):
    target = '../' + week['path']
    title = f"{week['week']}주차 · {week['title']}"
    return f'''<!DOCTYPE html>
<html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>최근 발표 · {escape(title)}</title><link rel="icon" href="data:,">
<link rel="canonical" href="{target}">
<script>location.replace(new URL({json.dumps(target)} + location.search + location.hash, location.href));</script>
<meta http-equiv="refresh" content="0;url={target}"></head>
<body><p>최근 발표자료로 이동한다. <a href="{target}">{escape(title)} 발표자료 열기</a></p></body></html>
'''


def write_archive(output, weeks):
    html = archive_html(weeks)
    redirect = redirect_html(published_weeks(weeks)[0])
    (output / 'index.html').write_text(html, encoding='utf-8')
    (output / 'latest').mkdir(exist_ok=True)
    (output / 'latest/index.html').write_text(redirect, encoding='utf-8')
