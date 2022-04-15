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
FRAME_RATE = 2

# VIDEOS FOLDER SETTINGS
CURRENT_DIR = str(pathlib.Path(__file__).parent.resolve())
FILE_LOCATION = 'source'

# VIDEO FILE SETTINGS
FILE_EXTENSION = '.mp4'
FILE_NAME_PATTERN = '(.*)\/source\/.*(\d{4}).*'

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


def video_to_frames(input_loc, output_loc):
    """Function to extract frames from input video file
    and save them as separate frames in an output directory.
    Args:
        input_loc: Input video file.
        output_loc: Output directory to save the frames.
        frame_rate: Number of frames to extract.
    Returns:
        None
    """
    if not os.path.exists(output_loc):
        if not create_folder(output_loc):
            return
    # Log the time
    time_start = time.time()
    # Start capturing the feed
    cap = cv2.VideoCapture(input_loc)
    # Find the number of frames
    video_length = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) - 1
    logging.info('Number of frames in video: ' + str(video_length))
    count = 0
    logging.info('Converting video ...')
    # Start converting the video
    while cap.isOpened():
        # Extract the frame
        ret, frame = cap.read()
        if not ret:
            continue
        # Write the results back to output location.
        cv2.imwrite(output_loc + "/%#05d.png" % (count + 1),
                    image_resize(frame, IMAGE_WIDTH, IMAGE_HEIGHT))
        count += 1
        # If there are no more frames left
        if count > (video_length - 1):
            # Log the time again
            time_end = time.time()
            # Release the feed
            cap.release()
            # Print stats
            logging.info(str(count) + ' frames extracted.')
            logging.info('It took ' + str(math.ceil(time_end - time_start)) +
                         ' seconds for conversion.')
            break


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
    for filename in glob.iglob(os.path.join(CURRENT_DIR, '**/**/**/**')):
        logging.info('Working with: ' + filename)
        match = re.search(FILE_NAME_PATTERN, filename, re.IGNORECASE)

        if not os.path.isfile(filename) or match == None:
            logging.warn(filename + " is not a file")
            continue

        curr_video_name = match.group(2)
        source_dir = match.group(1)
        if len(os.listdir(source_dir)) != 0:
            video_to_frames(filename, source_dir)
        else:
            logging.error('No files for ' + dir)
        logging.info('Processing of ' + curr_video_name + ' was finished\n')


def main():
    proceed_videos()


if __name__ == "__main__":
    main()
