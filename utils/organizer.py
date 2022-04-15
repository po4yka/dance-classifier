import os
import re
from pathlib import Path

PATH = Path(__file__).parent.resolve()
NAME_LENGTH = 4
FILE_EXTENSION = '.mp4'
file_format = re.compile('^\d{4}$')


def main():
    num = 1
    print(PATH)
    for filename in os.listdir(PATH):
        print('Working with file: ', filename)
        (file_name, file_extension) = os.path.splitext(filename)
        if file_extension == FILE_EXTENSION and not file_format.match(file_name):

            # rename file
            number_name = str(num).zfill(NAME_LENGTH)
            new_file_name = number_name + FILE_EXTENSION
            os.rename(os.path.join(PATH, filename),
                      os.path.join(PATH, new_file_name))

            # move file to the new folder
            dirName = os.path.join(PATH, number_name)
            if not os.path.exists(dirName):
                os.mkdir(dirName)
            else:
                print("ERROR: directory: ", dirName,  " already exists!")
            if not os.path.exists(dirName + '/source/'):
                os.mkdir(dirName + '/source/')
            else:
                print("ERROR: directory: ", dirName +
                      '/source/',  " already exists!")

            Path(os.path.join(PATH, new_file_name)).rename(
                os.path.join(dirName, 'source', new_file_name))

            num += 1

            print("FILE: " + filename + " was processed.")
        else:
            print('Incorrect file: ', filename)


if __name__ == "__main__":
    main()
