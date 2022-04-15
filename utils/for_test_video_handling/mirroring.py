import cv2
import os
import re
import time
import math
import pathlib
import logging
import coloredlogs
import glob

IMAGE_WIDTH = 1080
IMAGE_HEIGHT = 1920
IMAGE_PRECISION = 5
FRAME_RATE = 1

# VIDEOS FOLDER SETTINGS
CURRENT_DIR = str(pathlib.Path(__file__).parent.resolve())
FILE_LOCATION = 'source'

# VIDEO FILE SETTINGS
FILE_EXTENSION = '.mp4'

coloredlogs.install(level='DEBUG')


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


def clean_dir(dir_to_clean, frame_rate):
    files = os.listdir(dir_to_clean)
    files_to_save = files[::frame_rate]
    for file in files:
        target = os.path.join(dir_to_clean, file)
        if os.path.isfile(target) and file not in files_to_save:
            os.unlink(target)


def sp(num):
    if num == 1:
        return 0
    else:
        return 1


plural_video = ['video', 'videous']


def proceed_videos():
    logging.info('Current dir is ' + CURRENT_DIR)
    for filename in glob.iglob(os.path.join(CURRENT_DIR, "*")):
        file_name = os.path.basename(filename)
        logging.info('Working with: ' + os.path.basename(filename))
        _, file_extension = os.path.splitext(os.path.basename(file_name))

        if not os.path.isfile(filename) or file_extension != '.png':
            logging.warning(filename + " is not a handling instance")
            continue

        original_image = cv2.imread(filename)
        flip_horizontal = cv2.flip(original_image, 1)
        cv2.imwrite(filename, flip_horizontal)


def main():
    proceed_videos()


if __name__ == "__main__":
    main()
