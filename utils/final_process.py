import os
import re
import cv2
import shutil
import pathlib
import logging
import traceback
import coloredlogs

from typing import List
from argparse import ArgumentParser

# PATTERNS
VIDEO_FOLDER_PATTERN = r"^\d{4}$"
MOVE_PATTERN = r"move_\d*"
MOVE_SIDE_PATTERN = r"^(left|right)_\d*$"
PERSON_PATTERN = r"^person_\d*$"
PNG_EXT = ".png"

# STRINGS CONSTANTS
MOVES_FOLDER = "moves"

IMAGE_CANONICAL_WIDTH = 1080
IMAGE_CANONICAL_HEIGHT = 1920

ROOT_DIR = str(pathlib.Path(__file__).parent.resolve())

# How many times we can try to resize image to correct values
IMAGE_RESIZING_CALLS_LIMIT = 10

# Setup logger
logger = logging.getLogger(__name__)
coloredlogs.install(
    level=logging.DEBUG,
    logger=logger
)

# Assignments in runtime
result_folder_name = ""
result_folder_path = ""
moves_count = -1

# dict of persons counters for every move
persons_counter = {}


#############################
#   FOLDERS & FILES STUFF   #
#############################

def get_root_folder_name() -> str:
    return os.path.normpath(ROOT_DIR).split(os.path.sep)[-1]


# noinspection DuplicatedCode
def create_folder(path):
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


def create_result_folder() -> bool:
    """
    Creates result folder and folders for all moves_n

    Returns:
        True if all folders' creation succeeded and False if not

    """
    global result_folder_name
    global result_folder_path
    parent_folder = str(pathlib.Path(__file__).parent.parent.resolve())
    result_folder_name = get_root_folder_name() + "_processed"
    result_folder_path = os.path.join(parent_folder, result_folder_name)
    if not create_folder(result_folder_path):
        return False
    for i in range(1, moves_count + 1):
        move_dir_name = f"move_{i}"
        move_dir_path = os.path.join(result_folder_path, move_dir_name)
        if not create_folder(move_dir_path):
            return False

    return True


def get_new_person_dir_and_name(src_dir: str, move: str) -> str:
    """

    Args:
        move: name of move for which new person folder is needed
        src_dir: folder in which person folder is creating

    Returns:
        Tuple(person_folder_name, person_folder_path)
    """
    global persons_counter
    persons_counter[move] += 1
    person_folder_name = f'person_{persons_counter[move]:04d}'
    person_folder_path = os.path.join(src_dir, person_folder_name)
    return person_folder_path


def copy_files(src_path: str, src_files: List[str], dst_path: str):
    files_counter = 1
    for file_name in src_files:
        file_full_path = os.path.join(dst_path, f'{files_counter:04d}')
        if not file_full_path.endswith(PNG_EXT):
            file_full_path += PNG_EXT
        shutil.copy2(os.path.join(src_path, file_name), file_full_path,
                     follow_symlinks=True)
        files_counter += 1


##############################
#   IMAGE PROCESSING STUFF   #
##############################

def resize_img(path) -> bool:
    image = cv2.imread(path)
    img_height, img_width, _ = image.shape
    vertical_borders = int((IMAGE_CANONICAL_HEIGHT - img_height) / 2)
    horizontal_borders = int((IMAGE_CANONICAL_WIDTH - img_width) / 2)

    vertical_coefficient = IMAGE_CANONICAL_HEIGHT - vertical_borders * 2 - img_height
    horizontal_coefficient = IMAGE_CANONICAL_WIDTH - \
        horizontal_borders * 2 - img_width

    logger.info(
        "Handling: " + path + " (img_height == " + str(img_height) + "; img_width == " +
        str(img_width) + ")\n" +
        "with params vertical_borders == " + str(vertical_borders) +
        " horizontal_borders == " + str(horizontal_borders) +
        " vertical_coefficient == " + str(vertical_coefficient) +
        " horizontal_coefficient == " + str(horizontal_coefficient)
    )

    if vertical_borders < 0 or horizontal_borders < 0 or vertical_coefficient < 0 or horizontal_coefficient < 0:
        logger.warning("Image size is more than needed: img_height == " +
                       str(img_height) + "; img_width == " + str(img_width) + ")\n")
        cap = cv2.VideoCapture(path)
        _, frame = cap.read()
        cv2.imwrite(path, image_resize(
            frame, IMAGE_CANONICAL_WIDTH, IMAGE_CANONICAL_HEIGHT))
        cap.release()
        if img_height > IMAGE_CANONICAL_HEIGHT:
            resize_height = IMAGE_CANONICAL_HEIGHT
        else:
            resize_height = img_height
        if img_width > IMAGE_CANONICAL_WIDTH:
            resize_width = IMAGE_CANONICAL_WIDTH
        else:
            resize_width = img_height

        resized_image = cv2.resize(
            image, (resize_width, resize_height), interpolation=cv2.INTER_AREA)
        cv2.imwrite(path, resized_image)

        return False

    image = cv2.copyMakeBorder(image, vertical_borders, vertical_borders + vertical_coefficient,
                               horizontal_borders, horizontal_borders + horizontal_coefficient,
                               cv2.BORDER_REPLICATE, None, value=0)
    cv2.imwrite(path, image)

    return True


def check_and_resize(path):
    img = cv2.imread(path)
    if not os.path.isfile(path) or img is None:
        logger.error(
            "Try to handle non-existent file: " + path
        )
        for line in traceback.format_stack():
            print(line.strip())
        return
    height, width, _ = img.shape
    if height != IMAGE_CANONICAL_HEIGHT or width != IMAGE_CANONICAL_WIDTH:
        call_counter = 0
        call_result = resize_img(path)
        while not call_result and call_counter < IMAGE_RESIZING_CALLS_LIMIT:
            call_result = resize_img(path)
            call_counter += 1


def image_resize(image, width=None, height=None, inter=cv2.INTER_AREA):
    # initialize the dimensions of the image to be resized and
    # grab the image size
    dim = None
    (h, w) = image.shape[:2]

    # if both the width and height are None, then return the
    # original image
    if width is None and height is None:
        return image

    # check to see if the width is None
    if width is None:
        # calculate the ratio of the height and construct the
        # dimensions
        r = height / float(h)
        dim = (int(w * r), height)

    # otherwise, the height is None
    else:
        # calculate the ratio of the width and construct the
        # dimensions
        r = width / float(w)
        dim = (width, int(h * r))

    # resize the image
    resized = cv2.resize(image, dim, interpolation=inter)

    # return the resized image
    return resized


def process_files_sizes(folder_path: str, files: List[str]):
    for file_name in sorted(files):

        # Handle only .png files
        (_, ext) = os.path.splitext(file_name)
        if ext.lower() != PNG_EXT:
            continue

        check_and_resize(os.path.join(folder_path, file_name))


def handle_move_sides_with_creation(curr_folder: str, folders: List[str], dst_person_folder: str) -> bool:
    if not create_folder(dst_person_folder):
        logger.error(
            "Something went wrong with person folder creation!\nCreating folder path: " +
            dst_person_folder
        )
        return False
    if not handle_move_side(curr_folder, folders, dst_person_folder):
        logger.error(
            "Something went wrong with move side folder creation!\nIn folder: " + dst_person_folder
        )
        return False

    return True


def handle_move_side(curr_folder: str, folders: List[str], dst_person_folder: str) -> bool:
    files_counter = 1

    dst_person_left_folder_path = os.path.join(dst_person_folder, "left")
    dst_person_right_folder_path = os.path.join(dst_person_folder, "right")
    if not create_folder(dst_person_left_folder_path) or not create_folder(dst_person_right_folder_path):
        return False

    for folder in folders:
        if folder.startswith("left") or folder.startswith("right"):
            curr_dir_str_path = os.path.join(curr_folder, folder)
            curr_dir_path = os.fsencode(curr_dir_str_path)
            for file in os.listdir(curr_dir_path):
                filename = os.fsdecode(file)
                if not filename.endswith(PNG_EXT):
                    continue
                if folder.startswith("left"):
                    dst_side_folder = dst_person_left_folder_path
                else:
                    dst_side_folder = dst_person_right_folder_path
                final_img_path = os.path.join(
                    dst_side_folder, f'{files_counter:04d}{PNG_EXT}')
                shutil.copy2(
                    os.path.join(os.path.join(curr_dir_str_path, filename)),
                    final_img_path,
                    follow_symlinks=True
                )
                if os.path.isfile(final_img_path):
                    check_and_resize(final_img_path)
                    original_image = cv2.imread(final_img_path)
                    flip_horizontal = cv2.flip(original_image, 1)
                    if original_image is not None and flip_horizontal is not None:
                        if folder.startswith("left"):
                            cv2.imwrite(os.path.join(dst_person_right_folder_path,
                                                     f'{files_counter:04d}{PNG_EXT}'), flip_horizontal)
                        else:
                            cv2.imwrite(os.path.join(dst_person_left_folder_path,
                                                     f'{files_counter:04d}{PNG_EXT}'), flip_horizontal)
                        files_counter += 1
                    else:
                        logger.error("Non-exists files: original_image == " + str(original_image) +
                                     " or flip_horizontal == " + str(flip_horizontal))
        else:
            logger.error("Incorrect side folder name: " +
                         folder + "; in: " + curr_folder)
            return False

    return True


def handle_person(curr_folder: str, folders: List[str], move: str) -> bool:
    if folders:
        dst_person_folder = get_new_person_dir_and_name(
            os.path.join(result_folder_path, move), move)
        return handle_move_sides_with_creation(curr_folder, folders, dst_person_folder)
    else:
        logger.info("Handling folder with only files: " + curr_folder)
        dst_folder = get_new_person_dir_and_name(
            os.path.join(result_folder_path, move), move)
        if not create_folder(dst_folder):
            logger.error(
                "Something went wrong with person folder creation!\nCreating folder path: " + dst_folder)
            return False
        sub_files = [name for name in os.listdir(curr_folder)
                     if os.path.isfile(os.path.join(curr_folder, name))]
        copy_files(curr_folder, sub_files, dst_folder)
        new_sub_files = [name for name in os.listdir(dst_folder)
                         if os.path.isfile(os.path.join(dst_folder, name))]
        process_files_sizes(dst_folder, new_sub_files)

    return True


def handle_move(curr_folder: str, folders: List[str], files: List[str]) -> bool:
    move_name = os.path.normpath(curr_folder).split(os.path.sep)[-1]
    if folders:
        contains_person = False
        contains_move_side = False
        move_side_match = re.search(MOVE_SIDE_PATTERN, folders[0])
        person_match = re.search(PERSON_PATTERN, folders[0])
        if person_match is not None:
            contains_person = True
        if move_side_match is not None:
            contains_move_side = True

        if contains_person:
            for person_folder in folders:
                person_folder_path = os.path.join(curr_folder, person_folder)
                sub_folders = [name for name in os.listdir(person_folder_path)
                               if os.path.isdir(os.path.join(person_folder_path, name))]
                handle_person(person_folder_path, sub_folders, move_name)
        if contains_move_side:
            dst_person_folder = get_new_person_dir_and_name(
                os.path.join(result_folder_path, move_name), move_name)
            return handle_move_sides_with_creation(curr_folder, folders, dst_person_folder)
    else:
        logger.info("Handling folder with only files: " + curr_folder)
        dst_folder = get_new_person_dir_and_name(
            os.path.join(result_folder_path, move_name), move_name)
        if not create_folder(dst_folder):
            logger.error(
                "Something went wrong with person folder creation!\nCreating folder path: " + dst_folder)
            return False
        copy_files(curr_folder, files, dst_folder)
        sub_files = [name for name in os.listdir(dst_folder)
                     if os.path.isfile(os.path.join(dst_folder, name))]
        process_files_sizes(dst_folder, sub_files)

    return True


def handle_dir(curr_folder: str, folders: List[str], files: List[str]) -> bool:
    # fix for mac os specific case
    files: List[str] = list(
        filter(lambda file: not file.startswith("._"), files))

    if curr_folder == ROOT_DIR:  # exit if root folder
        return True

    root_folder_name = os.path.normpath(curr_folder).split(os.path.sep)[-1]
    video_folder_match = re.search(VIDEO_FOLDER_PATTERN, root_folder_name)
    if video_folder_match is not None:  # handled video folder

        # Handle incorrect cases
        if not folders and not files:
            logger.error("EMPTY video folder: " + curr_folder)
            return False
        if folders and files:
            logger.error("In " + curr_folder + " folder exists FOLDER(S) AND FILE(S): files == " + str(files) +
                         "; folders == " + str(folders))
            return False

        if folders:
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

            # Hierarchy: Move -> Person -> Side
            if contains_move:
                for move_folder in folders:
                    move_folder_path = os.path.join(curr_folder, move_folder)
                    sub_folders = [name for name in os.listdir(move_folder_path)
                                   if os.path.isdir(os.path.join(move_folder_path, name))]
                    sub_files = [name for name in os.listdir(move_folder_path)
                                 if os.path.isfile(os.path.join(move_folder_path, name))]
                    handle_move(move_folder_path, sub_folders, sub_files)
            if contains_person:
                for person_fold in folders:
                    person_folder_path = os.path.join(curr_folder, person_fold)
                    sub_folders = [name for name in os.listdir(person_folder_path)
                                   if os.path.isdir(os.path.join(person_folder_path, name))]
                    handle_person(person_folder_path, sub_folders, "move_1")
            if contains_move_side:
                # move_1 - creating folder for person from handling video in final single folder
                dst_person_folder = get_new_person_dir_and_name(
                    os.path.join(result_folder_path, "move_1"), "move_1")
                return handle_move_sides_with_creation(curr_folder, folders, dst_person_folder)

        else:  # have only one move for video and images is in a root folder
            logger.info("Handling folder with only files: " + curr_folder)
            # move_1 - creating folder for person from handling video in final single folder
            dst_folder = get_new_person_dir_and_name(
                os.path.join(result_folder_path, "move_1"), "move_1")
            if not create_folder(dst_folder):
                logger.error(
                    "Something went wrong with person folder creation!\nCreating folder path: " + dst_folder)
                return False
            copy_files(curr_folder, files, dst_folder)
            process_files_sizes(dst_folder, files)

        logger.info("Folder " + curr_folder + " handled succeeded!")

    return True


def main():
    # Setup command line argument
    global moves_count
    parser = ArgumentParser()
    parser.add_argument("-m", "--moves",
                        type=int,
                        default=-1,
                        help="count of moves in dance (default = -1)")

    # Handle moves count command line argument
    args = parser.parse_args()
    moves_count = args.moves
    if moves_count <= 0:
        parser.print_help()
        logger.error("Count of moves can't be less than or equal to zero")
        return

    if not create_result_folder():
        logger.error("Something went wrong with result folder creation!")
        return

    # different person counters for different moves
    for i in range(1, moves_count + 1):
        persons_counter[f'move_{i}'] = 0

    for current_folder, folders, files in os.walk(ROOT_DIR, topdown=True, followlinks=False):
        folders.sort()  # sort for easily perceived order
        # if something went wrong -> stop processing
        if not handle_dir(current_folder, folders, files):
            logger.error("Unable to process folder: " + current_folder)
            break


if __name__ == "__main__":
    main()
