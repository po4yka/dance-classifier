import os
import pathlib

ROOT_DIR = str(pathlib.Path(__file__).parent.resolve())


def main():
    counter = 1
    for current_folder, folders, files in os.walk(ROOT_DIR, topdown=True, followlinks=False):
        folders.sort()
        for folder in folders:
            if folder.startswith("person"):
                os.rename(folder, f'person_{counter:05d}')
                counter += 1


if __name__ == "__main__":
    main()
