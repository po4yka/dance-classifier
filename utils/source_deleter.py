import os
import sys
import shutil
import pathlib

ROOT_DIR = str(pathlib.Path(__file__).parent.resolve())
SOURCE_FOLDER = 'source'


def main():
    print('ROOT DIR == ' + ROOT_DIR)
    for root, _, _ in os.walk(ROOT_DIR):
        if root.endswith(SOURCE_FOLDER):
            print(root)
            shutil.rmtree(root, ignore_errors=True)


if __name__ == "__main__":
    main()
