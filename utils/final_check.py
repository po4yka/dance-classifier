import os
import re
import sys
import pathlib
import logging
import coloredlogs

from typing import List

# PATTERNS
VIDEO_FOLDER_PATTERN = r"^\d{4}$"
MOVE_PATTERN = r"move_\d*"
MOVE_SIDE_PATTERN = r"^(left|right)_\d*$"
PERSON_PATTERN = r"^person_\d*$"
PNG_EXT = ".png"

MOVES_FOLDER = "moves"

ROOT_DIR = str(pathlib.Path(__file__).parent.resolve())

logger = logging.getLogger(__name__)
coloredlogs.install(
    level=logging.DEBUG,
    logger=logger,
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)


def check_dir(root: str, dirs: List[str], files: List[str]):
    """

    Args:
        root: current checking root folder
        dirs: directories in current checking folder
        files: files in current checking folder

    Returns: None

    """
    # fix for mac os specific case
    files: List[str] = list(filter(lambda file: not file.startswith("._"), files))
    # check top level root folder
    if root == ROOT_DIR:
        for dir_name in dirs:
            video_folder_match = re.search(VIDEO_FOLDER_PATTERN, dir_name)
            if video_folder_match is None and dir_name != MOVES_FOLDER:
                logger.error("In " + root + " folder exists INCORRECT folder: " + dir_name)
        return
    if not dirs and not files:
        logger.error("EMPTY folder: " + root)
        return

    root_folder_name = os.path.normpath(root).split(os.path.sep)[-1]
    video_folder_match = re.search(VIDEO_FOLDER_PATTERN, root_folder_name)
    if video_folder_match is not None:
        if dirs and files:
            logger.error("In " + root + " folder exists FOLDER(S) AND FILE(S): files == " + str(files) +
                         "; folders == " + str(dirs))
            return
        contains_move = False
        contains_move_side_or_person = False
        for dir_name in dirs:
            move_match = re.search(MOVE_PATTERN, dir_name)
            move_side_match = re.search(MOVE_SIDE_PATTERN, dir_name)
            person_folder_match = re.search(PERSON_PATTERN, dir_name)

            if move_side_match is None and person_folder_match is None and move_match is None:
                logger.error("In " + root + " folder exists INCORRECT FOLDER: " + dir_name)
            if move_match is not None:
                contains_move = True
            if move_side_match is not None or person_folder_match is not None:
                contains_move_side_or_person = True

        if contains_move and contains_move_side_or_person:
            logger.error("In " + root + " folder INCORRECT FOLDER HIERARCHY: " + str(dirs))

        for file_name in files:
            # fix for mac os specific case
            if file_name.startswith("._"):
                continue
            (_, ext) = os.path.splitext(file_name)
            if ext.lower() != PNG_EXT:
                logger.error("In " + root + " folder exists file with INCORRECT EXTENSION: " + file_name)

    logger.info("Folder " + root + " check succeeded!")


def main():
    logger.info('Root directory is: ' + ROOT_DIR)
    for root, dirs, files in os.walk(ROOT_DIR, topdown=True):
        check_dir(root, dirs, files)


if __name__ == "__main__":
    main()
