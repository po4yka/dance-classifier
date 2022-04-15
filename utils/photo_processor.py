import os
import cv2
from pathlib import Path

CURR_PATH = Path(__file__).parent.resolve()

NAME_LENGTH = 4
FILE_EXTENSION = '.png'

IMAGE_WIDTH = 1080
IMAGE_HEIGHT = 1920

# other side name, if empty - no need
OTHER_SIDE_NAME = "left"


def rename_file(path, filename, curr_num):
    # rename file
    number_name = str(curr_num).zfill(NAME_LENGTH)
    new_file_name = number_name + FILE_EXTENSION
    os.rename(os.path.join(path, filename),
              os.path.join(path, new_file_name))

    Path(os.path.join(path, filename)).rename(
        os.path.join(path, new_file_name))

    curr_num += 1


def resize_img(path):
    image = cv2.imread(path)
    img_height, img_width, _ = image.shape
    vertical_borders = int((IMAGE_HEIGHT - img_height) / 2)
    horizontal_borders = int((IMAGE_WIDTH - img_width) / 2)

    vertical_coefficient = IMAGE_HEIGHT - vertical_borders * 2 - img_height
    horizontal_coefficient = IMAGE_WIDTH - horizontal_borders * 2 - img_width

    image = cv2.copyMakeBorder(image, vertical_borders, vertical_borders + vertical_coefficient,
                               horizontal_borders, horizontal_borders + horizontal_coefficient,
                               cv2.BORDER_REPLICATE, None, value=0)
    cv2.imwrite(path, image)


def check_and_resize(path):
    img = cv2.imread(path)
    height, width, _ = img.shape
    if height != IMAGE_HEIGHT or width != IMAGE_WIDTH:
        resize_img(path)


def process_img_in_folder(path):
    print('Working with path: ', path)
    num = 1
    for filename in os.listdir(path):
        (_, file_extension) = os.path.splitext(filename)
        if file_extension == FILE_EXTENSION:
            print('Working with file: ', filename)
            # rename_file(path, filename, num)
            check_and_resize(os.path.join(path, filename))

            num += 1
        else:
            print('Not processing file format: ', filename)


def main():
    process_img_in_folder(CURR_PATH)


if __name__ == "__main__":
    main()
