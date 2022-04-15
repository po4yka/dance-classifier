import os
import cv2
import sys
import logging
import pathlib
import coloredlogs

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)
coloredlogs.install(
    logger=logger,
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

ROOT_DIR = str(pathlib.Path(__file__).parent.resolve())

FLIPPED_FOLDER = "flipped"


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


def main():
    result_folder = os.path.join(ROOT_DIR, FLIPPED_FOLDER)
    create_folder(result_folder)
    for file in os.listdir(ROOT_DIR):
        if os.path.isfile(file) and file.endswith(".png"):
            final_img_path = os.path.join(ROOT_DIR, file)
            original_image = cv2.imread(final_img_path)
            flip_horizontal = cv2.flip(original_image, 1)
            if original_image is not None and flip_horizontal is not None:
                cv2.imwrite(os.path.join(result_folder, file), flip_horizontal)


if __name__ == "__main__":
    main()
