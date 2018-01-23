from PIL import Image
import requests
import urllib
from io import BytesIO


def get_image_from_url(url):
    response = requests.get(url)
    img = Image.open(BytesIO(response.content))
    return img


def get_image_from_url_as_bytes(url):
    resource = urllib.request.urlopen(url)
    return resource.read()
