"""Cut the week 6 clips and stills from the rendered Isaac runs (ffmpeg only).

    python prepare_clips.py /path/to/forklift

Inputs (paths relative to the robot repository):
- artifacts/20261004_slam_s3/seed_1/slam_online_three_panel.mp4 -- online SLAM
  mission, seed 1 (ws1 artifacts/20261004_slam_s3/seed_1, job 808), 60 fps,
  video time = simulation time.
- videos-from-ws1/20261006T1124Z_p5_slam_seed1_n1_planning_memory_no_pocket_check/
  and ..._n2_... -- LiDAR obstacle grid runs (ws1 l5_video14_nopc, jobs 1324/1327/1328),
  30 fps, video time = simulation time.
- videos-from-ws1/20261006T0431Z_p5_slam_seed1_n2_new_obstacle/ -- the same
  scenario before the planning memory (ws1 l5_video3).

Outputs in assets/:
- 44_mission_overview.mp4 / 45_slam_error.mp4: the SLAM mission (S3 seed 1) split in two --
  the overhead panel alone, online map with the live SLAM / wheel-odometry error text.
- 41_new_obstacle.mp4: new box on the transport path (spawn 73.2 s, replan 83.6 s) at 1.5x,
  overhead and online map panels side by side.
- 42_memory_compare.mp4: the overhead panel from just after the first return plan,
  before (0431Z, return plan 246.5 s) and with the memory (1124Z, 221.6 s), side by side;
  5.5 s only, so the first return plan stays on screen (the new boxes appear later).
- 43_camera_far.jpg / 43_camera_near.jpg: the carriage camera at 1.10 m and 0.03 m
  from the pallet (1124Z N1, 39 s and 43 s).
- 43_before_far.jpg / 43_before_near.jpg: the earlier fixed mount on the same task
  (artifacts/20261003_render/seed_2001, rendered before the selectable mount existed;
  16 s approaching, 19.5 s during insertion with the pallet out of view).
"""
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
FONT = '/usr/share/fonts/noto-cjk/NotoSansCJK-Bold.ttc'
PANEL1 = 'crop=620:620:20:70'          # overhead panel of the 1920 x 1080 composite


def run(args):
    subprocess.run(['ffmpeg', '-v', 'error', '-y', *args], check=True)


def encode(extra, out, crf=28):
    return [*extra, '-an', '-c:v', 'libx264', '-crf', str(crf), '-pix_fmt', 'yuv420p', '-r', '30',
            '-movflags', '+faststart', str(out)]


def poster(video, at, out):
    run(['-ss', str(at), '-i', str(video), '-frames:v', '1', '-q:v', '3', str(out)])


def label(text, x, cover_x=0, cover_w=320):
    # cover the composite's own panel caption first
    return (f"drawbox=x={cover_x}:y=0:w={cover_w}:h=48:color=0x1b1f24:t=fill,"
            f"drawtext=fontfile={FONT}:text='{text}':x={x}:y=14:fontsize=30:fontcolor=white:"
            f"box=1:boxcolor=0x1b1f24cc:boxborderw=10")


def main(repo):
    a = HERE / 'assets'
    s3 = repo / 'artifacts/20261004_slam_s3/seed_1/slam_online_three_panel.mp4'
    v = repo / 'videos-from-ws1'
    n1 = v / '20261006T1124Z_p5_slam_seed1_n1_planning_memory_no_pocket_check'
    n2 = v / '20261006T1124Z_p5_slam_seed1_n2_planning_memory_no_pocket_check'
    old = v / '20261006T0431Z_p5_slam_seed1_n2_new_obstacle'


    # The SLAM mission split over two slides: the overhead panel alone (the
    # status text below it is left out), and the online map + live
    # SLAM/odometry error text (both at 12x).
    run(encode(['-i', str(s3), '-vf', f"{PANEL1},{label('주행 화면', 14)},setpts=PTS/12"], a / '44_mission_overview.mp4'))
    poster(a / '44_mission_overview.mp4', 25, a / '44_mission_overview_poster.jpg')
    run(encode(['-i', str(s3), '-vf', 'crop=620:770:650:70,setpts=PTS/12'], a / '45_slam_error.mp4'))
    poster(a / '45_slam_error.mp4', 29.5, a / '45_slam_error_poster.jpg')

    # Overhead + online map only (camera panels, error plot and status text left out).
    run(encode(['-ss', '66', '-t', '36', '-i', str(n1 / 'slam_online_three_panel.mp4'),
                '-vf', "crop=1250:620:20:70,"
                       f"{label('주행 화면', 14)},{label('SLAM 지도 · LiDAR 장애물', 644, 630, 500)},setpts=PTS/1.5"],
               a / '41_new_obstacle.mp4', crf=26))
    poster(a / '41_new_obstacle.mp4', 14, a / '41_new_obstacle_poster.jpg')

    run(encode(['-ss', '247.0', '-t', '5.5', '-i', str(old / 'slam_online_three_panel.mp4'),
                '-ss', '222.0', '-t', '5.5', '-i', str(n2 / 'slam_online_three_panel.mp4'),
                '-filter_complex',
                f"[0:v]{PANEL1},{label('기억 없음', 14)},pad=636:620:0:0:color=white[l];"
                f"[1:v]{PANEL1},{label('본 장애물 기억', 14)}[r];"
                '[l][r]hstack=inputs=2[o]',
                '-map', '[o]'], a / '42_memory_compare.mp4', crf=26))
    poster(a / '42_memory_compare.mp4', 3, a / '42_memory_compare_poster.jpg')

    before = repo / 'artifacts/20261003_render/seed_2001/camera_rgb.mp4'   # old mount (0.75, 0, 0.50 m), before carriage_low
    run(['-ss', '16', '-i', str(before), '-frames:v', '1', '-q:v', '2', str(a / '43_before_far.jpg')])
    run(['-ss', '19.5', '-i', str(before), '-frames:v', '1', '-q:v', '2', str(a / '43_before_near.jpg')])
    run(['-ss', '39', '-i', str(n1 / 'camera_rgb.mp4'), '-frames:v', '1', '-q:v', '2', str(a / '43_camera_far.jpg')])
    run(['-ss', '43', '-i', str(n1 / 'camera_rgb.mp4'), '-frames:v', '1', '-q:v', '2', str(a / '43_camera_near.jpg')])
    # Slide 3: week 5's map clip (30 s, already 8x) 2.5x faster again, ~12 s.
    run(encode(['-i', str(a / '21_slam_map_pair.mp4'), '-vf', 'setpts=PTS/2.5'], a / '21_slam_map_pair_fast.mp4', crf=24))
    poster(a / '21_slam_map_pair_fast.mp4', 11.5, a / '21_slam_map_pair_fast_poster.jpg')
    print('done')


if __name__ == '__main__':
    main(Path(sys.argv[1]))
