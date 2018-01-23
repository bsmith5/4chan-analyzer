import errno
import os
import urllib
import basc_py4chan
from image import image_processor
from vision import google_cloud_vision

# setup directory to store files if necessary and make it my cwd
cwd = os.getcwd()
tmp_dir = os.path.join(cwd, 'tmpimages')

if os.path.isdir(tmp_dir):
    os.chdir(tmp_dir)
else:
    os.mkdir(tmp_dir, 775)
    os.chdir(tmp_dir)

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


def get_images_from_threads(max_images):
    i = 1
    for thread in threads:
        if i == max_images:
            return
        else:
            i = i + 1

        for file_object in thread.file_objects():

            try:
                content = image_processor.get_image_from_url_as_bytes(file_object.file_url)
                google_cloud_vision.get_labels(content)
            except ConnectionResetError as e:
                if e.errno != errno.ECONNRESET:
                    raise  # re-raise the last exception because it wasn't a conn reset
                else:
                    print("ConnectionResetError: skipping file", file_object.filename_original)
                    return
    return


def cleanup():
    for trash in os.listdir(tmp_dir):
        file_name_rm = os.path.join(tmp_dir, trash)
        os.remove(file_name_rm)


#get_files_from_threads(1)
#content = image_processor.get_image_from_url_as_bytes('http://xiostorage.com/wp-content/uploads/2015/10/test.png')
#google_cloud_vision.get_labels(content)
get_images_from_threads(4)
cleanup()
