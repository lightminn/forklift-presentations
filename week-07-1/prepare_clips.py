"""Cut the meeting deck's clips and stills (ffmpeg only).

    python prepare_clips.py depth  DIR   # DIR holds depth_raw.mp4, depth_stamps.json, near_tracking.json
    python prepare_clips.py mission DIR  # DIR holds the recorded run (slam_online_three_panel.mp4)

depth -- the S4b smoke run (forklift b66271f, ws1 artifacts/20261011_s4b/smoke/seed_1_v0.055: measured
  chassis, near-field tracking with the 1.0 m and 0.6 m corrections, D5 off). Its near-field depth reads
  (run/pocket_frames, 506 reads at 10 Hz, 30.38-80.88 s) were coloured on ws1 by depth_clip/render_depth.py
  into depth_raw.mp4 (ws1 artifacts/20261011_meeting_video/depth_clip, video time = stamp - first stamp).
  The tracker's events (run/near_tracking.json) are written over the frames for about 3 s each, the last
  frame is held 3.2 s, then the clip is played at 2x -> assets/61_insert_depth.mp4.
mission -- the recorded mission (ws1 artifacts/20261011_meeting_video/seed_N_d7: the d7 arm of
  artifacts/20261008_d7_isaac with --video --robot-camera; near-field tracking is off because its
  measured bounds condition requires video off) -> assets/71_mission.mp4 (overhead panel) and stills.

Clips reused from week 6 (already in assets/, cut by week-06/prepare_clips.py): 45_slam_error.mp4,
46_new_obstacle_single.mp4, 43_camera_far/near.jpg, 43_before_far/near.jpg.
"""
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
FONT = '/usr/share/fonts/noto-cjk/NotoSansCJK-Bold.ttc'
PANEL1 = 'crop=620:620:20:70'          # overhead panel of the 1920 x 1080 three-panel composite


def run(args):
    subprocess.run(['ffmpeg', '-v', 'error', '-y', *args], check=True)


def encode(extra, out, crf=26):
    return [*extra, '-an', '-c:v', 'libx264', '-crf', str(crf), '-pix_fmt', 'yuv420p', '-r', '30',
            '-movflags', '+faststart', str(out)]


def poster(video, at, out):
    run(['-ss', str(at), '-i', str(video), '-frames:v', '1', '-q:v', '3', str(out)])


def text(t, start, end, y=18, size=30):
    return (f"drawtext=fontfile={FONT}:text='{t}':x=(w-text_w)/2:y={y}:fontsize={size}:fontcolor=white:"
            f"box=1:boxcolor=0x1b1f24d9:boxborderw=12:enable='between(t,{start:.2f},{end:.2f})'")


# The tracker's events, as shown on the clip (near_tracking.json events / corrections).
EVENT_TEXT = {   # numbered as the step strip beside the clip (build_deck.py slide 6)
    'armed': '② 근접 추적 시작',
    'correction:1.0': '③ 앞면 1.0 m 보정',
    'correction:0.6': '③ 앞면 0.6 m 보정',
    'protect': '④ 포켓 벽 간격 감시',
    'insert_end_arrival': '⑤ 삽입 끝',
}
HOLD_S = 3.2


def depth(src):
    src = Path(src)
    stamps = json.loads((src / 'depth_stamps.json').read_text())
    t0, t_end = stamps[0][0], stamps[-1][0]
    near = json.loads((src / 'near_tracking.json').read_text())
    marks = []
    for event in near['events']:
        key = event['event']
        if key == 'correction_trigger':
            key = f"correction:{event['point_m']:.1f}"
        if key in EVENT_TEXT:
            marks.append((event['time_s'] - t0, EVENT_TEXT[key]))
    marks.sort()
    filters = [f'tpad=stop_mode=clone:stop_duration={HOLD_S}']   # hold the insertion end on screen
    for i, (start, words) in enumerate(marks):
        last = i + 1 == len(marks)
        end = t_end - t0 + HOLD_S + 1 if last else min(start + HOLD_S, marks[i + 1][0])
        filters.append(text(words, start, end))
    filters.append(f"drawtext=fontfile={FONT}:text='깊이 영상 · 빨강 가까움 · 파랑 멂':x=w-text_w-14:y=h-text_h-14:"
                   f"fontsize=22:fontcolor=white:box=1:boxcolor=0x1b1f24b0:boxborderw=8")
    out = HERE / 'assets/61_insert_depth.mp4'
    run(encode(['-i', str(src / 'depth_raw.mp4'), '-vf', ','.join(filters) + ',setpts=PTS/2'], out, crf=24))
    poster(out, (marks[1][0] + 0.8) / 2 if len(marks) > 1 else 5, HERE / 'assets/61_insert_depth_poster.jpg')
    print('events', [(round(s, 2), w) for s, w in marks])


def label(text, x, cover_x=0, cover_w=320):
    # cover the composite's own panel caption first (as week 6)
    return (f"drawbox=x={cover_x}:y=0:w={cover_w}:h=48:color=0x1b1f24:t=fill,"
            f"drawtext=fontfile={FONT}:text='{text}':x={x}:y=14:fontsize=30:fontcolor=white:"
            f"box=1:boxcolor=0x1b1f24cc:boxborderw=10")


def mission(src):
    """Scene 5 of the recorded runs: the overhead panel of the three-panel composite at 12x,
    and a still of the hall at the start (transport.mp4, 1280 x 720) for slide 5."""
    src = Path(src)
    out = HERE / 'assets/71_mission.mp4'
    run(encode(['-i', str(src / 'slam_online_three_panel.mp4'),
                '-vf', f"{PANEL1},{label('주행 화면', 14)},setpts=PTS/12"], out))
    poster(out, 8, HERE / 'assets/71_mission_poster.jpg')
    run(['-ss', '0.5', '-i', str(src / 'transport.mp4'), '-frames:v', '1', '-vf', 'crop=700:720:290:0',
         '-q:v', '2', str(HERE / 'assets/70_hall.jpg')])


if __name__ == '__main__':
    {'depth': depth, 'mission': mission}[sys.argv[1]](sys.argv[2])
