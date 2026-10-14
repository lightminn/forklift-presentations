"""Cut the meeting deck's clips and stills (ffmpeg; the depth clip's stage labels with PIL).

    python prepare_clips.py depth    DIR   # DIR holds depth_raw.mp4, depth_stamps.json, near_tracking.json
    python prepare_clips.py mission  DIR   # DIR holds slam_online_three_panel_clean.mp4 and transport.mp4
    python prepare_clips.py obstacle FILE  # the clean composite of the week 6 box run
    python prepare_clips.py slam     FILE  # the clean composite of the S3 SLAM run (with the odometry path)

No colour meanings are written into the clips: the slides carry them as graphic legends
(build_deck.py legend()). The depth clip has a small stage label in the top-left corner
(prepare_reverse_clip.caption); the composites have no text over the views at all.

depth -- the S4b smoke run (forklift b66271f, ws1 artifacts/20261011_s4b/smoke/seed_1_v0.055: measured
  chassis, near-field tracking with the 1.0 m and 0.6 m corrections, D5 off). Its near-field depth reads
  (run/pocket_frames, 506 reads at 10 Hz, 30.38-80.88 s) were coloured on ws1 by depth_clip/render_depth.py
  into depth_raw.mp4 (ws1 artifacts/20261011_meeting_video/depth_clip, turbo, 0.25 m red to 3.0 m blue,
  no return black; video time = stamp - first stamp). The tracker's events (run/near_tracking.json) are
  labelled for about 3 s each, the last frame is held 3.2 s, then the clip is played at 2x ->
  assets/61_insert_depth.mp4. The 640 x 480 frames are cropped to 548 x 480 (floor at the sides) so the
  clip fills its panel at the stage height.

The composites (mission, obstacle, slam) are the recorded online-SLAM runs composed again on ws1 without
burned-in text (artifacts/20261012_meeting_clean: compose/compose_online_slam_video.py is forklift df109cf's
composer with the title, panel captions, replan / new-obstacle banners, the "새 장애물" tag and the legend
line taken out, the error readouts renamed; meeting_clean.sbatch, jobs 2413-2415). Nothing is simulated
again; the paths, maps, cells and boxes are drawn from the same records as before.
mission -- ws1 artifacts/20261011_meeting_video/seed_5_d7 (the d7 arm of artifacts/20261008_d7_isaac with
  --video --robot-camera; near-field tracking is off because its measured bounds condition requires video
  off): the overhead panel at 12x -> assets/71_mission.mp4, and the hall still from transport.mp4.
obstacle -- ws1 artifacts/20261005_p5_l3/l8_measured/seed_5_n1 (week 6 slide 7, snapshot p5_df109cf): the
  overhead and map panels, 73-118 s at 2x -> assets/46_new_obstacle_single.mp4.
slam -- since 2026-10-14 the measured-chassis mission run (the same record as mission: ws1
  artifacts/20261012_return_forward/seed_5_fwd7) composed again in ws1 artifacts/20261014_meeting_slam
  (meeting_slam.sbatch, job 2603: the deck composer + --draw-odometry --clean-map --draw-pallet --stride 24,
  so no plan lines or grid cells as on the S3 clip it replaces, the pallet footprint at its recorded pose,
  and only the frames the 12x clip keeps): the map panel with its two error readouts, at 12x ->
  assets/45_slam_error.mp4. Before: artifacts/20261004_slam_s3/seed_1 (week 6 slide 5, provisional chassis).
"""
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PANEL1 = 'crop=620:620:20:70'          # overhead panel of the 1920 x 1080 three-panel composite
PANELS12 = 'crop=1250:620:20:70'       # overhead + map panels
MAP_READOUT = 'crop=620:708:650:70'    # map panel and the two error readouts under it
DEPTH_X, DEPTH_W, DEPTH_H = 46, 548, 480   # the depth panel's aspect at the stage height (slide 10)
HALL_CROP = 'crop=568:720:356:0'       # the hall still's aspect at the stage height (slide 8)


def run(args):
    subprocess.run(['ffmpeg', '-v', 'error', '-y', *args], check=True)


def encode(extra, out, crf=26):
    return [*extra, '-an', '-c:v', 'libx264', '-crf', str(crf), '-pix_fmt', 'yuv420p', '-r', '30',
            '-movflags', '+faststart', str(out)]


def poster(video, at, out):
    run(['-ss', str(at), '-i', str(video), '-frames:v', '1', '-q:v', '3', str(out)])


# The tracker's events, as labelled on the clip (near_tracking.json events / corrections).
EVENT_TEXT = {   # numbered as the step table beside the clip (build_deck.py, 삽입 중 포켓 추적)
    'armed': '포켓 추적 개시',   # armed in front mode: not the table's step ② (roof tracking)
    'correction:1.0': '③ 경로 보정 · 1.0 m',
    'correction:0.6': '③ 경로 보정 · 0.6 m',
    'protect': '④ 간격 감시',
    'insert_end_arrival': '⑤ 삽입 완료',
}
HOLD_S = 3.2
DEPTH_FPS = 10


def depth(src):
    import numpy as np
    from PIL import Image
    import prepare_reverse_clip as rc
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
    spans = []
    for i, (start, words) in enumerate(marks):
        last = i + 1 == len(marks)
        end = t_end - t0 + HOLD_S + 1 if last else min(start + HOLD_S, marks[i + 1][0])
        spans.append((start, end, words))

    def label(tt):
        on = [w for a, b, w in spans if a <= tt <= b]
        return on[-1] if on else None

    W, H = 640, 480
    out = HERE / 'assets/61_insert_depth.mp4'
    dec = subprocess.Popen(['ffmpeg', '-v', 'error', '-i', str(src / 'depth_raw.mp4'), '-f', 'rawvideo',
                            '-pix_fmt', 'rgb24', '-'], stdout=subprocess.PIPE)
    enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24',
                            '-s', f'{DEPTH_W}x{DEPTH_H}', '-r', str(2 * DEPTH_FPS), '-i', '-', '-an',   # 2x
                            '-c:v', 'libx264', '-crf', '24', '-pix_fmt', 'yuv420p', '-r', '30',
                            '-movflags', '+faststart', str(out)], stdin=subprocess.PIPE)
    poster_k = round((marks[1][0] + 0.8) * DEPTH_FPS) if len(marks) > 1 else 50
    k, frame = 0, None
    while True:
        buf = dec.stdout.read(W * H * 3)
        if len(buf) < W * H * 3:
            break
        frame = np.ascontiguousarray(np.frombuffer(buf, np.uint8).reshape(H, W, 3)[:, DEPTH_X:DEPTH_X + DEPTH_W])
        words = label(k / DEPTH_FPS)
        img = np.ascontiguousarray(rc.caption(frame, words, size=21)) if words else frame
        enc.stdin.write(img.tobytes())
        if k == poster_k:
            Image.fromarray(img).save(HERE / 'assets/61_insert_depth_poster.jpg', quality=88)
        k += 1
    for j in range(round(HOLD_S * DEPTH_FPS)):          # hold the insertion end on screen
        words = label((k + j) / DEPTH_FPS)
        img = np.ascontiguousarray(rc.caption(frame, words, size=21)) if words else frame
        enc.stdin.write(img.tobytes())
    dec.stdout.close()
    dec.wait()
    enc.stdin.close()
    enc.wait()
    print('frames', k, 'events', [(round(s, 2), w) for s, w in marks])


def mission(src):
    """Scene 5 of the recorded runs: the overhead panel of the clean composite at 12x, and a still
    of the hall at the start (transport.mp4, 1280 x 720) for the simulation slide."""
    src = Path(src)
    out = HERE / 'assets/71_mission.mp4'
    run(encode(['-i', str(src / 'slam_online_three_panel_clean.mp4'), '-vf', f'{PANEL1},setpts=PTS/12'], out))
    poster(out, 8, HERE / 'assets/71_mission_poster.jpg')
    run(['-ss', '0.5', '-i', str(src / 'transport.mp4'), '-frames:v', '1', '-vf', HALL_CROP,
         '-q:v', '2', str(HERE / 'assets/70_hall.jpg')])


def obstacle(composite):
    """The week 6 box run (spawn 77.2 s, stop ~78 s, replan 94.3 s, then reverse): overhead + map, 2x."""
    out = HERE / 'assets/46_new_obstacle_single.mp4'
    run(encode(['-ss', '73', '-t', '45', '-i', str(composite), '-vf', f'{PANELS12},setpts=PTS/2'], out))
    poster(out, 5, HERE / 'assets/46_new_obstacle_single_poster.jpg')


def slam(composite):
    """The SLAM mission's map panel with the SLAM and odometry error readouts, 12x (the composite may be
    strided: its frame rate already carries the stride, so the same filter keeps real-time x 12)."""
    out = HERE / 'assets/45_slam_error.mp4'
    run(encode(['-i', str(composite), '-vf', f'{MAP_READOUT},setpts=PTS/12'], out, crf=28))
    poster(out, 20.0, HERE / 'assets/45_slam_error_poster.jpg')


if __name__ == '__main__':
    {'depth': depth, 'mission': mission, 'obstacle': obstacle, 'slam': slam}[sys.argv[1]](sys.argv[2])
