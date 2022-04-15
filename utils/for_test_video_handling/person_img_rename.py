import os
import pathlib

ROOT_DIR = str(pathlib.Path(__file__).parent.resolve())


def main():
    counter = 1
    for file in os.listdir(ROOT_DIR):
        if (file.endswith('.png')):
            os.rename(file, f'{counter:05d}.png')
            counter += 1


if __name__ == "__main__":
    main()
