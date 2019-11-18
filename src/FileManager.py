import os
import json
import random
from enum import Enum

parent_folder = os.path.abspath(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

with open(os.path.join(parent_folder, "etc", "manager")) as f:
    manager = int(f.readline().replace("\n", ""))


class DATASET(Enum):
    USERS = os.path.join(parent_folder, "dataset", "datausers.json")
    ORIGINAL = os.path.join(parent_folder, "dataset", "dataset.json")
    WORKING = os.path.join(parent_folder, "dataset", "dataset_working.json")
    LABELED = os.path.join(parent_folder, "dataset", "dataset_labeled.json")


_pending_ = "pending"


def load_dataset(which_dataset):
    with open(which_dataset.value) as f:
        dataset = json.load(f)
    return dataset


def write_dataset(which_dataset, dataset):
    with open(which_dataset.value, "w") as f:
        f.write(json.dumps(dataset, sort_keys=True, indent=4))


def next_image(dataset=None):
    """
    Get the next unlabeled image from the dataset of labeled images
    It marks the image with a "pending" state label while it is being classified.
    """
    if dataset is None:
        dataset = load_dataset(DATASET.WORKING)
    keys = list(dataset.keys())
    image = None
    for _ in range(len(keys)):
        k = random.choice(keys)
        v = dataset[k]
        if v["label"] is None:
            v["label"] = _pending_
            image = (k, v)
            break
    # Just to ensure there is no more unlabeled lambs
    if image is None:
        for k, v in dataset.items():
            if v["label"] is None:
                v["label"] = _pending_
                image = (k, v)
                break
    if image is not None:
        write_dataset(DATASET.WORKING, dataset)
        return image, dataset
    else:
        print("we didn't find and image!")
        # raise Exception("Not image found")
        return None


def update_current_photo_user(id_user, next_photo, last_photo_label=None, user_data=None, working_dataset=None,
                              labeled_dataset=None):
    """
    Upload the current image asigned to a specific user in the dictionary.
    Saves the label of the last imaged which was asigned to that user.
    """
    id_user = str(id_user)
    # Get the dataset of users-photos dictionary
    if user_data is None:
        user_data = load_dataset(DATASET.USERS)
    changes = []
    if id_user in user_data.keys() and last_photo_label is not None:
        if user_data[id_user][1]["label"] in (None, _pending_):
            # Collect the pending changes to-do in the image's dataset
            changes.append((user_data[id_user][0], last_photo_label))
        else:
            print("User ", id_user, " is trying to change the photo ",
                  user_data[id_user], " with no info")
    # Prepare next photo in the dataset of users-photos dictionary
    #   and discard the last image asigned to the user if it was the case
    user_data[id_user] = next_photo
    user_data[id_user][1]["label"] = _pending_
    changes.append((next_photo[0], _pending_))
    # Update the dataset of labeled images json file
    update_image(changes, working_dataset, labeled_dataset)

    # Save the current dataset of users-photos dictionary
    write_dataset(DATASET.USERS, user_data)


def update_last_photo(id_user, user_data=None, working_dataset=None, labeled_dataset=None):
    # Get the dataset of users-photos dictionary
    id_user = str(id_user)
    if user_data is None:
        user_data = load_dataset(DATASET.USERS)

    if id_user in user_data.keys():
        update_image(changes=[(user_data[id_user][0], None)], working_dataset=working_dataset, labeled_dataset=labeled_dataset)

        # Remove the user from the users-photo dictionary
        user_data.pop(id_user, None)

        # Save the current dataset of users-photos dictionary
        write_dataset(DATASET.USERS, user_data)


def update_image(changes, working_dataset=None, labeled_dataset=None):
    """
    It uploads the label of a specific image in the dataset of images
    """
    if working_dataset is None:
        working_dataset = load_dataset(DATASET.WORKING)
    if labeled_dataset is None and changes[0][1] not in (None, _pending_):
        labeled_dataset = load_dataset(DATASET.LABELED)

    for id_photo, value in changes:
        if value in (None, _pending_):
            if working_dataset[id_photo]["label"] in (None, _pending_):
                working_dataset[id_photo]["label"] = value
            else:
                try:
                    working_dataset.pop(id_photo, None)
                except:
                    pass
        else:
            if working_dataset[id_photo]["label"] in (None, _pending_):
                image = working_dataset.pop(id_photo, None)
                if image is not None:
                    image["label"] = value
                    labeled_dataset[id_photo] = image
            else:
                raise Exception("Trying to change the label of a labeled image")

    if working_dataset is not None:
        write_dataset(DATASET.WORKING, working_dataset)
    if labeled_dataset is not None:
        write_dataset(DATASET.LABELED, labeled_dataset)
