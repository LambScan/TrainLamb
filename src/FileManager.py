import os
import json
import random

parent_folder = os.path.abspath(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
__dataset_conf_file__ = os.path.join(parent_folder, "dataset", "dataset.json")
__users_data__ = os.path.join(parent_folder, "dataset", "datausers.json")
_pending_ = "pending"


def next_image(dataset=None):
    """
    Get the next unlabeled image from the dataset of labeled images
    It marks the image with a "pending" state label while it is being classified.
    """
    if dataset is None:
        with open(__dataset_conf_file__, "r") as f:
            dataset = json.load(f)
    keys = list(dataset.keys())
    image = None
    for _ in range(len(keys)):
        k = random.choice(keys)
        v = dataset[k]
        if v["label"] is None:
            v["label"] = _pending_
            image = (k, v)
            break
    if image is not None:
        with open(__dataset_conf_file__, "w") as f:
            f.write(json.dumps(dataset, sort_keys=True, indent=4))
        return image
    else:
        print("we didn't find and image!")
        raise Exception("Not image found")


def update_current_photo_user(id_user, next_photo, last_photo_label=None, user_data=None):
    """
    Upload the current image asigned to a specific user in the dictionary.
    Saves the label of the last imaged which was asigned to that user.
    """
    id_user = str(id_user)
    # Get the dataset of users-photos dictionary
    if user_data is None:
        with open(__users_data__, "r") as f:
            user_data = json.load(f)
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
    update_image(changes)

    # Save the current dataset of users-photos dictionary
    with open(__users_data__, "w") as f:
        f.write(json.dumps(user_data, sort_keys=True, indent=4))


def update_last_photo(id_user, last_photo_label=None, user_data=None):
    # Get the dataset of users-photos dictionary
    id_user = str(id_user)
    if user_data is None:
        with open(__users_data__, "r") as f:
            user_data = json.load(f)

    if id_user in user_data.keys():
        update_image([(user_data[id_user][0], None)])

        # Remove the user from the users-photo dictionary
        try:
            user_data.pop(id_user, None)
        except KeyError as e:
            print("Error trying to delete the user ", id_user)
            print(e)
            print(type(e))

        # Save the current dataset of users-photos dictionary
        with open(__users_data__, "w") as f:
            f.write(json.dumps(user_data, sort_keys=True, indent=4))


def update_image(changes, dataset=None):
    """
    It uploads the label of a specific image in the dataset of images
    """

    if dataset is None:
        with open(__dataset_conf_file__, "r") as f:
            dataset = json.load(f)

    for id_photo, value in changes:
        if dataset[id_photo]["label"] in (None, _pending_):
            dataset[id_photo]["label"] = value
        else:
            raise Exception("Trying to change the label of a labeled image")

    with open(__dataset_conf_file__, "w") as f:
        f.write(json.dumps(dataset, sort_keys=True, indent=4))


if __name__ == "__main__":
    next_image()
