"""Crop the RoboWorld booth photos for the week 11-1 deck (EXIF dropped on save).

    /home/light/anaconda3/bin/python prepare_photos.py <folder with the KakaoTalk_*.jpg photos>

The photos are the team's own (Galaxy, 2026-11-06/07). Crops are in original pixels (4000 x 3000).
"""
import sys
from pathlib import Path
from PIL import Image, ImageOps

OUT = Path(__file__).resolve().parent / 'assets'
CROPS = {
    # Multiway Robotics lineup chart: title to the series row; customer logos and the finger left out
    'v02_multiway.jpg': ('KakaoTalk_20261111_074831204.jpg', (300, 110, 3940, 1880), 1600),
    # H3R poster: title, the 6-phase motor and the dual 3-phase ESC diagram
    'v03_h3r.jpg': ('KakaoTalk_20261111_074822969_01.jpg', (1220, 640, 3080, 1810), 1400),
    # FASTECH Ezi-Pos booth: the AGV/AMR drive, the servo racks, the maxon motors and the drive shelf
    'v04_ezipos.jpg': ('KakaoTalk_20261111_085705697.jpg', (260, 720, 3360, 2480), 1600),
}


def main(src):
    src = Path(src)
    for name, (photo, box, width) in CROPS.items():
        im = ImageOps.exif_transpose(Image.open(src / photo)).convert('RGB').crop(box)
        im = im.resize((width, round(im.height * width / im.width)), Image.LANCZOS)
        im.save(OUT / name, quality=85, optimize=True)   # no exif= argument: metadata is not carried over
        print(name, im.size)


if __name__ == '__main__':
    main(sys.argv[1])
