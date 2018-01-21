import io
import os
import urllib
import errno
import basc_py4chan
from google.cloud import vision
from google.cloud.vision import types

# setup directory to store files if necessary and make it my cwd
cwd = os.getcwd()
tmp_dir = os.path.join(cwd, 'tmpimages')

if os.path.isdir(tmp_dir):
    os.chdir(tmp_dir)
else:
    os.mkdir(tmp_dir, 775)
    os.chdir(tmp_dir)

# instantiate the google vision client
vision_client = vision.ImageAnnotatorClient()

# get all threads from specified 4chan board
board = basc_py4chan.Board("g", https=False, session=None)
threads = board.get_all_threads(expand=False)


def get_files_from_threads(max_files):
    # download all the files from all of those threads to tmpdir
    i = 1
    for thread in threads:
        if i == max_files:
            return
        else:
            i = i + 1

        for file_object in thread.file_objects():

            if os.path.isfile(file_object.filename_original):
                continue
            else:
                try:
                    urllib.request.urlretrieve(file_object.file_url, file_object.filename_original)
                except ConnectionResetError as e:
                    if e.errno != errno.ECONNRESET:
                        raise  # re-raise the last exception because it wasn't a conn reset
                    else:
                        print("ConnectionResetError: skipping file", file_object.filename_original)
                        return
    return


# TODO this is probably better refactored to take the fully qualified filename as an argument
# also wouldn't hurt to sanitize input of unsupported file types
# for each image call the google image processing api to gather facts
def call_vision_api():

    for file in os.listdir(tmp_dir):

        # The name of the image file to annotate
        file_name = os.path.join(tmp_dir, file)

        # Loads the image into memory
        with io.open(file_name, 'rb') as image_file:
            content = image_file.read()

        image = types.Image(content=content)

        # Performs label detection on the image file
        response = vision_client.label_detection(image=image)
        labels = response.label_annotations

        # persist to datastore
        # TODO find a cloud datastore and put this in it instead of printing
        print('Filename:', file_name)
        print('Labels:')
        for label in labels:
            print(label.description)


def cleanup():
    for trash in os.listdir(tmp_dir):
        file_name_rm = os.path.join(tmp_dir, trash)
        os.remove(file_name_rm)


get_files_from_threads(5)
call_vision_api()
cleanup()
