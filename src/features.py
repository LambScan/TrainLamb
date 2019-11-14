import os
from datetime import datetime
import cv2
import numpy as np
import time
from telepot.namedtuple import ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton
from FileManager import next_image, update_current_photo_user, update_last_photo, parent_folder, __dataset_conf_file__, \
    __users_data__

custom_keyboard = [["\U0001F411 One complete lamb \U0001F411",
                    "\U0001F342 Empty \U0001F342"],
                   ["\U0001F984 Not exactly one complete lamb \U0001F984",
                    "\U0001F99F Error / Dirty / A fly \U0001F99F"],
                   ["\U0001F937 I don't know \U0001F937", "\U0001F195 Next one \U0001F195"]]
reply_markup = ReplyKeyboardMarkup(keyboard=custom_keyboard)


def get_image(depth_path, color_path=None):
    depth_path = os.path.join(parent_folder, *depth_path.split("/"))
    # color_path = os.path.join(parent_folder, *color_path.split("/"))

    depth_image = cv2.imread(depth_path, cv2.IMREAD_ANYDEPTH)
    # color_image = cv2.imread(color_path)
    depth_image = cv2.applyColorMap(255 - np.ubyte(depth_image), cv2.COLORMAP_HOT)
    return depth_image


def normal_execution(TelegramBot, user_id, last_photo_label=None):
    # Query the next to-label image to show
    image_dict = next_image()
    # Make a new image by stacking the two images
    image = get_image(depth_path=image_dict[1]["path_depth"], color_path=image_dict[1]["path_color"])
    # Update the assigned photo to this user and save the last label
    if last_photo_label is None:
        update_current_photo_user(id_user=user_id, next_photo=image_dict)
    else:
        print("We're changing the label to: ", last_photo_label)
        update_current_photo_user(id_user=user_id, next_photo=image_dict, last_photo_label=last_photo_label)

    # Send the next photo
    TelegramBot.sendMessage(chat_id=user_id,
                            text="What do you see in the following picture?")
    send_photo(TelegramBot=TelegramBot, user_id=user_id, image=image)


def send_photo(TelegramBot, user_id, path=None, image=None):
    if path is None and image is not None:
        temp_path = str(str(datetime.now()) + "_temp.png")
        cv2.imwrite(temp_path, image)
        TelegramBot.sendPhoto(chat_id=user_id,
                              photo=open(temp_path, "rb"),
                              reply_markup=reply_markup)
        os.remove(temp_path)
    elif path is not None and image is None:
        TelegramBot.sendPhoto(chat_id=user_id,
                              photo=open(path, "rb"),
                              reply_markup=reply_markup)
    else:
        print("No arguments for sending the picture")
        raise Exception("No arguments for sending the picture!.")


def start(TelegramBot, user_id):
    TelegramBot.sendMessage(chat_id=user_id,
                            text="\U0001F411 \U0001F411 \U0001F411 \U0001F411 \U0001F411")
    time.sleep(1)
    TelegramBot.sendMessage(chat_id=user_id,
                            text="We're trying to sort out a dataset to train a neural network \U0001F9E0 with a bunch of lamb's images.\U0001F411 \nWe only discriminate 4 options:")
    time.sleep(2)
    TelegramBot.sendMessage(chat_id=user_id,
                            text=" \U0001F4BB These are the 4 options availables: \U0001F913")
    time.sleep(2)
    TelegramBot.sendMessage(chat_id=user_id,
                            text="1. \U0001F411 A pretty little lamb. \U0001F411 \nThe image must contain the full animal, end to end; the head and the tail.")
    time.sleep(1)
    TelegramBot.sendMessage(chat_id=user_id,
                            text="A few examples:")
    send_photo(TelegramBot, user_id=user_id,
               path=os.path.join(parent_folder, *"/dataset/examples/lamb_0.png".split("/")))
    time.sleep(1)
    send_photo(TelegramBot, user_id=user_id,
               path=os.path.join(parent_folder, *"/dataset/examples/lamb_1.png".split("/")))
    time.sleep(2)
    TelegramBot.sendMessage(chat_id=user_id,
                            text="\U0001F411 ...We may send you a few grown sheeps \U0001F40F. If they are in the right position, it's also ok \U0001F44D.")
    time.sleep(2)
    TelegramBot.sendMessage(chat_id=user_id,
                            text="A few examples:")
    time.sleep(1)
    send_photo(TelegramBot, user_id=user_id,
               path=os.path.join(parent_folder, *"/dataset/examples/sheep_0.png".split("/")))
    time.sleep(1)
    send_photo(TelegramBot, user_id=user_id,
               path=os.path.join(parent_folder, *"/dataset/examples/sheep_1.png".split("/")))

    time.sleep(2)
    TelegramBot.sendMessage(chat_id=user_id,
                            text="2. \U0001F342 An empty space. \U0001F341 \nThere is no lamb \U0001F463 or anything like a little lamb. \U0001F342")
    time.sleep(1)
    TelegramBot.sendMessage(chat_id=user_id,
                            text="A few examples:")
    send_photo(TelegramBot, user_id=user_id,
               path=os.path.join(parent_folder, *"/dataset/examples/empty_1.png".split("/")))
    time.sleep(1)
    send_photo(TelegramBot, user_id=user_id,
               path=os.path.join(parent_folder, *"/dataset/examples/empty_0.png".split("/")))
    time.sleep(2)
    TelegramBot.sendMessage(chat_id=user_id,
                            text="3. \U0001F984 Wrong position.\n \U0001F42E There is more than one lamb in the picture, or there is only the head of our lamb \U0001F418, or the butt... but there is not a full body of a lamb. \U0001F984")
    TelegramBot.sendMessage(chat_id=user_id,
                            text="A few examples:")
    time.sleep(1)
    send_photo(TelegramBot, user_id=user_id,
               path=os.path.join(parent_folder, *"/dataset/examples/dirty_head.png".split("/")))
    time.sleep(1)
    send_photo(TelegramBot, user_id=user_id,
               path=os.path.join(parent_folder, *"/dataset/examples/dirty_2lambs.png".split("/")))
    time.sleep(1)
    TelegramBot.sendMessage(chat_id=user_id,
                            text="4. ...a fly.   \U0001F99F \nYes.\n \U0001F997 There are a lot of flys \U0001F4A9 in the farm; they use our cameras to everything they can possibly imagine \U0001F4A9. We're still working on it.\n \U0001F577 If you get an image which you can't interpretate \U0001F47B or just partially interpretate, please, \U0001F578 label it as a dirty image,\U0001F4A9 an error, a fly. \U0001F99F")
    time.sleep(1)
    TelegramBot.sendMessage(chat_id=user_id,
                            text="A few examples:")
    time.sleep(1)
    send_photo(TelegramBot, user_id=user_id,
               path=os.path.join(parent_folder, *"/dataset/examples/dirty_lamb.png".split("/")))
    time.sleep(1)
    send_photo(TelegramBot, user_id=user_id, path=os.path.join(parent_folder, *"/dataset/examples/fly.png".split("/")))
    time.sleep(1)
    TelegramBot.sendMessage(chat_id=user_id,
                            text="\U0001F411 That's it. Let's see the lambs! \U0001F411 \U0001F411")
    TelegramBot.sendMessage(chat_id=user_id,
                            text="\U0001F411 \U0001F411 \U0001F411 \U0001F411 \U0001F411")

    time.sleep(3)
    normal_execution(TelegramBot, user_id)


def stop(TelegramBot, user_id):
    # Upload dataset's labels: "pending" to None
    update_last_photo(id_user=user_id, last_photo_label=None)
    TelegramBot.sendMessage(chat_id=user_id,
                            text="Bot stopped",
                            reply_markup=ReplyKeyboardRemove())


def restart(TelegramBot, user_id):
    # The same thing that with the stop function but without sending the stop message
    update_last_photo(id_user=user_id, last_photo_label=None)
    start(TelegramBot, user_id)


def upload_info(TelegramBot, user_id, label):
    normal_execution(TelegramBot, user_id, label)


def ignore(TelegramBot, user_id):
    # Query the next to-label image to show
    image_dict = next_image()
    # Make a new image by stacking the two images
    image = get_image(color_path=image_dict[1]["path_color"], depth_path=image_dict[1]["path_depth"])

    # The same thing that with the stop function but without sending the stop message
    update_last_photo(id_user=user_id, last_photo_label=None)

    # Update the assigned photo to this user and save the last label
    update_current_photo_user(id_user=user_id, next_photo=image_dict)

    # Send the next photo
    cv2.imwrite("temp.png", image)
    current_msg = TelegramBot.sendPhoto(chat_id=user_id,
                                        photo=open("temp.png", "rb"),
                                        reply_markup=reply_markup)
    os.remove("temp.png")
