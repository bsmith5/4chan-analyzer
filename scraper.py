import io
import os
import urllib
import basc_py4chan
from google.cloud import vision

# setup directory to store files if necessary and make it my cwd
tmpdir="tmpimages"

if os.path.isdir(tmpdir):
    os.chdir(tmpdir)
else:
    os.mkdir(tmpdir, 775)
    os.chdir(tmpdir)

# setup vision client
vision_client = vision.Client()

# get all threads from specified 4chan board
board = basc_py4chan.Board("g", https=False, session=None)
threads = board.get_all_threads(expand=False)

# download all the files from all of those threads to tmpdir
for thread in threads:
    for file in thread.file_objects():
        urllib.request.urlretrieve(file.file_url, file.filename_original)

        # call the google image processing api to gather facts about these images
        with io.open(file.filename_original, 'rb') as image_file_name:
            content = image_file_name.read()
            image = vision_client.image(content=content)
    labels = image.detect_labels()

    # persist to datastore
    for label in labels:
        print(label.description)

# cleanup tmpdir
#os.rmdir(tmpdir)
