import os
import json
import random
from enum import Enum

parent_folder = os.path.abspath(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

with open(os.path.join(parent_folder, "etc", "manager")) as f:
    manager = int(f.readline().replace("\n", ""))

_pending_ = "pending"


class DATASET(Enum):
    USERS = os.path.join(parent_folder, "dataset", "datausers.json")
    ORIGINAL = os.path.join(parent_folder, "dataset", "dataset.json")
    WORKING = os.path.join(parent_folder, "dataset", "dataset_working.json")
    LABELED = os.path.join(parent_folder, "dataset", "dataset_labeled.json")


def load_dataset(which_dataset):
    with open(which_dataset.value) as f:
        dataset = json.load(f)
    return dataset


def write_dataset(which_dataset, dataset):
    with open(which_dataset.value, "w") as f:
        f.write(json.dumps(dataset, sort_keys=True, indent=4))


def get_info(user_id):
    user_id = str(user_id)
    datauser = load_dataset(DATASET.USERS)
    working = load_dataset(DATASET.WORKING)
    labeled = load_dataset(DATASET.LABELED)
    original = 80457  # load_dataset(DATASET.ORIGINAL)

    lamb_count = 0
    dirty_count = 0
    empty_count = 0
    wrong_count = 0
    for k, v in labeled.items():
        if v["label"] == "lamb":
            lamb_count += 1
        elif v["label"] == "empty":
            dirty_count += 1
        elif v["label"] == "wrong":
            empty_count += 1
        elif v["label"] == "fly":
            wrong_count += 1
    final_message = "There are {original} total images, {labeled} already labeled:\n" \
                    "   - {lamb_count} images with lambs \n" \
                    "   - {empty_count} empty images \n" \
                    "   - {wrong_count} images with lambs in a wrong position \n" \
                    "   - {dirty_count} dirty images / with flies \n" \
                    "\nThere are {working} images to sort out yet.\nThere are also " \
                    "{datauser} people using this bot.".format(original=original, labeled=len(labeled),
                                                               lamb_count=lamb_count, empty_count=empty_count,
                                                               wrong_count=wrong_count, dirty_count=dirty_count,
                                                               working=len(working), datauser=len(datauser))

    personal_msg = "You already sorted out {} lamb's images!".format(datauser[user_id]["counter"])

    return final_message, personal_msg


def get_ranking():
    datauser = load_dataset(DATASET.USERS)
    ranking = []
    for k, v in datauser.items():
        username = v.get("username", k)
        name = v.get("name", k)
        if username == k:
            ranking.append(("id: {}".format(k), int(v["counter"])))
        else:
            ranking.append(("{} (@{})".format(name, username), int(v["counter"])))

    return sorted(ranking, key=lambda x: x[1], reverse=True)


def get_current_image(user_id):
    user_id = str(user_id)
    userdata = load_dataset(DATASET.USERS)
    return userdata[user_id]["image"]


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
    counter = 0
    # Get the dataset of users-photos dictionary
    if user_data is None:
        user_data = load_dataset(DATASET.USERS)
    changes = []
    if id_user in user_data.keys() and last_photo_label is not None:
        if user_data[id_user]["image"][1]["label"] in (None, _pending_):
            # Collect the pending changes to-do in the image's dataset
            changes.append((user_data[id_user]["image"][0], last_photo_label))
            counter += 1
        else:
            print("User ", id_user, " is trying to change the photo ",
                  user_data[id_user], " with no info")
        counter = int(user_data[id_user].get("counter", 0))
        counter += 1
    # Prepare next photo in the dataset of users-photos dictionary
    #   and discard the last image asigned to the user if it was the case
    user_data[id_user] = {"image": next_photo}
    user_data[id_user]["image"][1]["label"] = _pending_
    user_data[id_user]["counter"] = counter
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
        update_image(changes=[(user_data[id_user]["image"][0], None)], working_dataset=working_dataset,
                     labeled_dataset=labeled_dataset)

        user_data[id_user]["image"][1]["label"] = None
        # Remove the user from the users-photo dictionary
        # user_data.pop(id_user, None)

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
