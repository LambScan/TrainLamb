import cv2
import os
from datetime import datetime
import cv2
import numpy as np
from telepot.namedtuple import ReplyKeyboardMarkup, ReplyKeyboardRemove
from src.FileManager import next_image, update_current_photo_user, update_last_photo

custom_keyboard = [["Lamb", "Empty"],
                   ["Error", "There's a fly\nor something"],
                   ["I don't know", "Next one"]]
reply_markup = ReplyKeyboardMarkup(keyboard=custom_keyboard)


def get_image(color_path, depth_path):
    # TODO: delete
    if not depth_path:
        depth_path = "/home/alberto/DataLamb/savings/color/error/2019-10-04/2019-10-04 11:35:10.818722_cam01_color.png"
    if not color_path:
        color_path = depth_path.replace("depth", "color")

    depth_path = str(os.path.dirname(os.getcwd()) + depth_path)
    color_path = str(os.path.dirname(os.getcwd()) + color_path)

    depth_image = cv2.imread(depth_path, cv2.IMREAD_ANYDEPTH)
    color_image = cv2.imread(color_path)
    depth_image = cv2.applyColorMap(cv2.convertScaleAbs(depth_image), cv2.COLORMAP_JET)
    return np.hstack((color_image, depth_image))


def normal_execution(TelegramBot, user_id, last_photo_label=None):
    # Query the next to-label image to show
    image_dict = next_image()
    # Make a new image by stacking the two images
    image = get_image(color_path=image_dict[1]["path_color"], depth_path=image_dict[1]["path_depth"])
    # Update the assigned photo to this user and save the last label
    if last_photo_label is None:
        update_current_photo_user(id_user=user_id, next_photo=image_dict)
    else:
        print("We're changing the label to: ", last_photo_label)
        update_current_photo_user(id_user=user_id, next_photo=image_dict, last_photo_label=last_photo_label)

    # Send the next photo
    temp_path = str(str(datetime.now()) + "_temp.png")
    cv2.imwrite(temp_path, image)
    TelegramBot.sendPhoto(chat_id=user_id,
                          photo=open(temp_path, "rb"),
                          reply_markup=reply_markup)
    os.remove(temp_path)


def start(TelegramBot, user_id):
    normal_execution(TelegramBot, user_id)


def stop(TelegramBot, user_id):
    # Upload dataset's labels: "pending" to None
    update_last_photo(id_user=user_id, last_photo_label=None)
    TelegramBot.sendMessage(chat_id=user_id,
                            text="Bot stopped",
                            reply_markup=ReplyKeyboardRemove())


def restart(TelegramBot, user_id):
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


def upload_info(TelegramBot, user_id, label):
    normal_execution(TelegramBot, user_id, label)


def ignore(TelegramBot, user_id):
    restart(TelegramBot, user_id)
