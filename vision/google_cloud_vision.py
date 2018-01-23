from google.cloud import vision
from google.cloud.vision import types


# instantiate the google vision client
vision_client = vision.ImageAnnotatorClient()


# call the google image processing api to gather facts about the content
def get_labels(content):

    # Sets the desired image type
    image = types.Image(content=content)

    # Performs label detection on the image
    response = vision_client.label_detection(image=image)
    labels = response.label_annotations

    # persist to datastore
    # TODO find a cloud datastore and put this in it instead of printing
    print('Labels:')
    for label in labels:
        print(label.description)
