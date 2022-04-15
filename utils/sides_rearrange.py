import os
import re
import sys
import shutil
import pathlib
import logging
import coloredlogs

from typing import List

# PATTERNS
MOVE_PATTERN = r"move_\d*"
MOVE_SIDE_PATTERN = r"^(left|right)$"
PERSON_PATTERN = r"^person_\d*$"
PNG_EXT = ".png"

ROOT_DIR = str(pathlib.Path(__file__).parent.resolve())

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)
coloredlogs.install(
    logger=logger,
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

result_folder_path = ""
result_folder_left_path = ""
result_folder_right_path = ""


# noinspection DuplicatedCode
def create_folder(path) -> bool:
    """Function to safe folder creation.
    Args:
        path: path for folder creation
    Returns:
        None
    """
    current_directory = os.getcwd()
    final_directory = os.path.join(current_directory, path)
    if not os.path.exists(final_directory):
        try:
            os.mkdir(path)
        except OSError:
            logging.error('Creation of the directory ' +
                          str(path) + ' failed!')
            return False
        else:
            logging.info('Successfully created the directory ' + str(path))
            return True


# noinspection DuplicatedCode
def handle_dir(curr_folder: str, folders: List[str], files: List[str]) -> bool:
    # fix for mac os specific case
    files: List[str] = list(
        filter(lambda working_file: not working_file.startswith("._"), files))

    # logger.info("Working with: " + curr_folder + ", folders: " + str(folders) + ", files: " + str(files))

    if curr_folder == ROOT_DIR:  # exit if root folder
        return True

    # Handle incorrect cases
    if not folders and not files:
        logger.error("EMPTY folder: " + curr_folder)
        return False
    if folders and files:
        logger.error("In " + curr_folder + " folder exists FOLDER(S) AND FILE(S): files == " + str(files) +
                     "; folders == " + str(folders))
        return False
    if not folders:
        logging.info("No folders folder handled")
        return True

    contains_move = False
    contains_person = False
    contains_move_side = False
    move_match = re.search(MOVE_PATTERN, folders[0])
    move_side_match = re.search(MOVE_SIDE_PATTERN, folders[0])
    person_match = re.search(PERSON_PATTERN, folders[0])
    if move_match is not None:
        contains_move = True
    if person_match is not None:
        contains_person = True
    if move_side_match is not None:
        contains_move_side = True

    global result_folder_path
    global result_folder_left_path
    global result_folder_right_path

    if contains_move:
        logging.info("Move folder handled")
        return True
    elif contains_person:
        logging.info("Person folder handled")
        return True
    elif contains_move_side:
        logging.info("Work with: " + curr_folder +
                     ", folders: " + str(folders))
        for folder in folders:
            split_path = os.path.normpath(curr_folder).split(os.path.sep)
            person_folder_name = split_path[-1]
            move_folder_name = split_path[-2]
            logging.info("Working with person_folder_name == " +
                         person_folder_name)
            if move_folder_name.startswith("move"):
                move_folder_path = os.path.join(
                    result_folder_path, move_folder_name)
                if not os.path.exists(move_folder_path):
                    create_folder(move_folder_path)
                logging.info(
                    "Working with move_folder_path == " + move_folder_path)
            else:
                move_folder_path = result_folder_path

            if folder.startswith("left") or folder.startswith("right"):
                side_folder_path = os.path.join(move_folder_path, folder)
                logging.info("Handling side_folder_path == " +
                             side_folder_path)
                if not os.path.exists(side_folder_path):
                    create_folder(side_folder_path)
                person_folder_path = os.path.join(
                    side_folder_path, person_folder_name)
                if not os.path.exists(person_folder_path):
                    create_folder(person_folder_path)

                curr_side_folder_path = os.path.join(curr_folder, folder)
                sub_files = [name for name in os.listdir(curr_side_folder_path)
                             if os.path.isfile(os.path.join(curr_side_folder_path, name))]
                for file in sub_files:
                    old_file_full_path = os.path.join(
                        curr_side_folder_path, file)
                    file_full_path = os.path.join(person_folder_path, file)
                    shutil.copy2(old_file_full_path,
                                 file_full_path, follow_symlinks=True)
                    logging.info('Successfully handled file: ' +
                                 old_file_full_path + " --> " + file_full_path)
            else:
                logging.info("Handling side_folder_path == " + folder)

        return True


def main():
    logger.info('Root directory is: ' + ROOT_DIR)

    global result_folder_path
    global result_folder_left_path
    global result_folder_right_path

    root_folder_name = os.path.normpath(ROOT_DIR).split(os.path.sep)[-1]
    parent_folder = str(pathlib.Path(__file__).parent.parent.resolve())
    result_folder_name = root_folder_name + "by_sides"
    result_folder_path = os.path.join(parent_folder, result_folder_name)

    if not create_folder(result_folder_path):
        logger.error("Can't create result folder!")
        return False

    for current_folder, folders, files in os.walk(ROOT_DIR, topdown=True, followlinks=True):
        folders.sort()
        handle_dir(current_folder, folders, files)


if __name__ == "__main__":
    main()
