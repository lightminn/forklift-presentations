#!/usr/bin/env python3
"""Create an independent draft from a previous week's presentation."""
import argparse
import json
import shutil
import subprocess
import sys
from weekly import ROOT, load_weeks, published_weeks, week_number


def create_week(number, title=None, source_number=None):
    destination = ROOT / f'week-{number:02d}'
    if destination.exists():
        raise SystemExit(f'already exists: {destination.name}; existing files were preserved')
    weeks = load_weeks(ROOT)
    if source_number is None:
        source = published_weeks(weeks)[0]
    else:
        source = next((week for week in weeks if week['week'] == source_number), None)
        if source is None:
            raise SystemExit(f'source week does not exist: {source_number}')
    if number <= source['week']:
        raise SystemExit('new week must be later than the source week')
    shutil.copytree(source['directory'], destination,
                    ignore=shutil.ignore_patterns('__pycache__', '*.pyc', '.DS_Store'))
    info = {'week': number, 'title': title or f'{number}주차 개발 진행 보고',
            'summary': '', 'status': 'draft'}
    (destination / 'week.json').write_text(json.dumps(info, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    (destination / 'VALIDATION.md').write_text(
        f'# {number}주차 발표자료 검증 기록\n\n미검증. {source["week"]}주차 자료를 복사한 초안이며, '
        '이전 주의 검증 결과는 이번 주에 적용하지 않는다.\n\n'
        '내용 수정 후 생성·배포 검사를 실행하고 1920 × 1080 전체화면에서 확인한 결과를 기록한다.\n', encoding='utf-8')
    sources = destination / 'SOURCES.md'
    if sources.exists():
        sources.write_text(f'> {source["week"]}주차에서 이어받은 출처 목록이다. 이번 주 내용에 맞게 갱신해야 한다.\n\n' + sources.read_text(encoding='utf-8'), encoding='utf-8')
    (destination / 'README.md').write_text(
        f'# {number}주차 발표자료 초안\n\n{source["week"]}주차의 본문·원고·이미지와 UOS 실행 파일을 독립 복사하였다.\n\n'
        '- `build_deck.py`: 표지, 본문, 발표 원고, 기준일, 시간 및 장수 검사를 이번 주 내용에 맞게 수정한다.\n'
        '- `week.json`: 목록에 표시할 제목과 요약을 작성한다. 현재 상태는 `draft`이다.\n'
        '- `SOURCES.md`, `VALIDATION.md`: 이번 주 출처와 실제 검증 결과를 기록한다.\n'
        '- 새 자료의 내용과 FHD 화면을 확인한 후 `status`를 `published`로 변경한다.\n\n'
        '전체 생성 및 배포 절차는 [레포 안내](../README.md)를 따른다.\n', encoding='utf-8')
    subprocess.run([sys.executable, str(destination / 'build_deck.py')], cwd=destination, check=True)
    print(f'Created {destination.name}/ as draft from week {source["week"]}.')
    print('이전 주 본문이 포함된 초안이다. 내용을 수정하고 검증한 후 week.json의 status를 published로 변경한다.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('week', type=week_number)
    parser.add_argument('--title')
    parser.add_argument('--from', dest='source_week', type=week_number)
    args = parser.parse_args()
    create_week(args.week, args.title, args.source_week)


if __name__ == '__main__':
    main()
