import os
import sys
import pathlib
from PIL import Image

ROOT_DIR = str(pathlib.Path(__file__).parent.resolve())
PNG_EXT = '.png'


def main():
    # print('ROOT DIR == ' + ROOT_DIR)
    # print('Enter coords for cut in the following order:', '\033[1m' + 'left, upper, right, lower' + '\033[0m' + ':')
    coords = list(map(int, sys.argv[1:]))
    if len(coords) != 4:
        print('Need 4 coords for cut')
        return
    for root, dirs, files in os.walk(ROOT_DIR):
        for name in files:
            # fix for mac os specific case
            if name.startswith("._"):
                continue
            (base, ext) = os.path.splitext(name)
            # print("base = ", base,  "; ext = ", ext, "; name = ", name)
            if ext.lower() == PNG_EXT:
                # print('File ==', name, '; coords ==', coords)
                Image.open(name).crop(coords).save(name)


if __name__ == "__main__":
    main()
