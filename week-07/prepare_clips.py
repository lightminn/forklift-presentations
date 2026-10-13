"""Cut the week 7 fleet clips and stills from the rendered Isaac runs (ffmpeg only).

    python3 prepare_clips.py /home/projects/forklift/artifacts [out_dir]

Runs where the renders are (ws1); out_dir defaults to ./assets. Inputs, relative
to the artifacts directory (robot repository branch feat/fleet-five):
- 20261008_fleet/runs/f2d_truth_seed0_overlay.mp4 -- five trucks on the full
  NVIDIA warehouse, fixed order + safe-stop rule, simulator pose, seed 0
  (ws1 job 1916; 1920 x 1080, video 258.5 s = simulation 517 s).
- 20261009_fleet_worlds/videos/tw24_{rack,shop,multi}600.mp4 -- eight trucks,
  eight people, a 60 s breakdown and a spill on the random factories, crossing
  time windows (v24, ws1 jobs 2441/2443/2445, composed 2442/2444/2446;
  1920 x 1080, video 400 s = simulation 1,200 s).
- <close dir>/close_rack600_composed.mp4 -- the same run as tw24_rack600 rendered
  again with the camera moved over two waits (source_v27 + --view-centre 47 40.4
  --view-across-m 36, ws1 job 2568; trajectories equal the original run to 0.0 m
  up to 405 s), composed by tools/compose_world_video.py --speed 1 (video time =
  simulation time). The waits (found with tools/explain_tablets.py --reason
  tablet / safe_stop, job 2564): T5 behind T2 from 236.3 s, T7 behind T1 from 349.8 s.

Every crop keeps the map only: the composite's title, status panel and caption
lines are dropped, and the slide draws the legend instead.
"""
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent

# Map region of each 1920 x 1080 composite (w:h:x:y), read off the frames.
WAREHOUSE = '1440:810:0:70'
RACK = '1056:752:192:98'
SHOP = '768:760:336:94'
MULTI = '1328:744:56:100'
CLOSE_A = '700:450:740:365'   # map (0, 70) + T5/T2 region
CLOSE_B = '700:450:50:95'    # map (0, 70) + T7/T1 region


def run(args):
    subprocess.run(['ffmpeg', '-v', 'error', '-y', *args], check=True)


def clip(src, out, crop, speed, width, start=0, length=None, crf=28):
    span = ['-ss', str(start)] + (['-t', str(length)] if length else [])
    run([*span, '-i', str(src), '-vf', f'crop={crop},setpts=PTS/{speed},scale={width}:-2,fps=30',
         '-an', '-c:v', 'libx264', '-crf', str(crf), '-pix_fmt', 'yuv420p', '-movflags', '+faststart', str(out)])
    poster = out.with_name(out.stem + '_poster.jpg')
    run(['-sseof', '-0.5', '-i', str(out), '-frames:v', '1', '-q:v', '3', str(poster)])


def still(src, out, crop, at, width):
    run(['-ss', str(at), '-i', str(src), '-vf', f'crop={crop},scale={width}:-2', '-frames:v', '1', '-q:v', '3', str(out)])


def main(art, out, explain):
    out.mkdir(exist_ok=True)
    worlds = art / '20261009_fleet_worlds/videos'
    # 3: five trucks, whole run at 4x more (8x simulation)
    clip(art / '20261008_fleet/runs/f2d_truth_seed0_overlay.mp4', out / '71_warehouse5.mp4', WAREHOUSE, 4, 1280)
    # 5: the three factory structures, mid-run (video 150 s = simulation 450 s)
    still(worlds / 'tw24_rack600.mp4', out / '73_rack.jpg', RACK, 150, 720)
    still(worlds / 'tw24_shop600.mp4', out / '73_shop.jpg', SHOP, 150, 540)
    still(worlds / 'tw24_multi600.mp4', out / '73_multi.jpg', MULTI, 150, 900)
    # 7: eight trucks on the rack warehouse, whole 1,200 s at 5x more (15x simulation)
    clip(worlds / 'tw24_rack600.mp4', out / '74_rack600.mp4', RACK, 5, 1056)
    # 4: the two waits, close up, at 3x
    close = explain / 'close_rack600_composed.mp4'
    clip(close, out / '72_close_a.mp4', CLOSE_A, 3, 860, start=230, length=52)
    clip(close, out / '72_close_b.mp4', CLOSE_B, 3, 860, start=344, length=58)


if __name__ == '__main__':
    art = Path(sys.argv[1])
    out = Path(sys.argv[2]) if len(sys.argv) > 2 else HERE / 'assets'
    explain = Path(sys.argv[3]) if len(sys.argv) > 3 else Path.home() / 'w7deck/exp/runs'
    main(art, out, explain)
