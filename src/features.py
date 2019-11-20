import os
import cv2
import time
from datetime import datetime
import numpy as np
from telepot.namedtuple import ReplyKeyboardMarkup, ReplyKeyboardRemove
from FileManager import next_image, update_current_photo_user, update_last_photo, parent_folder, manager, get_info, \
    get_current_image, get_ranking


def get_custom_keyboard():
    _ = list(options.keys())
    custom_keyboard = list(zip(_[::2], _[1::2]))
    custom_keyboard[-1] = custom_keyboard[-1] + ("\U0001F937 I don't know",)
    custom_keyboard[0] = custom_keyboard[0] + ("\U0001F914 Help",)
    # custom_keyboard.append(("\U0001F937 I don't know \U0001F937", "\U0001F195 Next one \U0001F195"))
    return ReplyKeyboardMarkup(keyboard=custom_keyboard)


def get_image(depth_path, color_path=None):
    depth_path = os.path.join(parent_folder, *depth_path.split("/"))
    # color_path = os.path.join(parent_folder, *color_path.split("/"))

    depth_image = cv2.imread(depth_path, cv2.IMREAD_ANYDEPTH)
    # color_image = cv2.imread(color_path)
    depth_image = cv2.applyColorMap(255 - np.ubyte(depth_image), cv2.COLORMAP_HOT)
    return depth_image


def normal_execution(TelegramBot, user, last_photo_label=None):
    # Query the next to-label image to show
    _ = next_image()
    if _ is not None:
        image_dict, working_dataset = _
        # Load the new depth image and apply a colormap
        image = get_image(depth_path=image_dict[1]["path_depth"])

        # Update the assigned photo to this user and save the last label
        if last_photo_label is None:
            update_current_photo_user(user=user, next_photo=image_dict, working_dataset=working_dataset)
        else:
            print("The user ", user[1], " (id: ", user[0], " is changing the label to: ", last_photo_label)
            update_current_photo_user(user=user, next_photo=image_dict, last_photo_label=last_photo_label,
                                      working_dataset=working_dataset)
            TelegramBot.sendMessage(chat_id=int(user[0]),
                                    text="Thanks. You're changing the image's label to: " + str(last_photo_label))
            time.sleep(1.3)
        # Send the next photo
        TelegramBot.sendMessage(chat_id=int(user[0]),
                                text="What do you see in the following picture?")
        send_photo(TelegramBot=TelegramBot, user=user, image=image)
    else:
        for user in manager:
            TelegramBot.sendMessage(chat_id=user,
                                    text="Labelling task finished")
            TelegramBot.sendMessage(chat_id=user,
                                    text="I repeat, the labelling task has finished")


def send_photo(TelegramBot, user, path=None, image=None):
    if path is None and image is not None:
        temp_path = str(str(datetime.now()) + "_temp.png")
        cv2.imwrite(temp_path, image)
        TelegramBot.sendPhoto(chat_id=int(user[0]),
                              photo=open(temp_path, "rb"),
                              reply_markup=get_custom_keyboard())
        os.remove(temp_path)
    elif path is not None and image is None:
        TelegramBot.sendPhoto(chat_id=int(user[0]),
                              photo=open(path, "rb"))
    else:
        print("No arguments for sending the picture")
        raise Exception("No arguments for sending the picture!.")


def stop(TelegramBot, user):
    final_message, personal_msg = get_info(user[0])

    # Upload dataset's labels: "pending" to None
    update_last_photo(user=user)
    TelegramBot.sendMessage(chat_id=int(user[0]),
                            text="\U0001F603 Thank you for your time feeding our system \U0001F44F \nYou're improving a still harmless AI... \U0001F608")
    TelegramBot.sendMessage(chat_id=int(user[0]),
                            text=personal_msg)
    TelegramBot.sendMessage(chat_id=int(user[0]),
                            text=final_message)
    TelegramBot.sendMessage(chat_id=int(user[0]),
                            text="Bot stopped",
                            reply_markup=ReplyKeyboardRemove())


def restart(TelegramBot, user):
    # The same thing that with the stop function but without sending the stop message
    update_last_photo(user=user)
    start(TelegramBot, user)


def upload_info(TelegramBot, user, label):
    normal_execution(TelegramBot, user, label)


def ignore(TelegramBot, user):
    # Query the next to-label image to show
    _ = next_image()
    if _ is not None:
        image_dict, working_dataset = _

        TelegramBot.sendMessage(chat_id=int(user[0]),
                                text="Ok, let's move on")

        # Load the new depth image and apply a colormap
        image = get_image(depth_path=image_dict[1]["path_depth"])

        # The same thing that with the stop function but without sending the stop message
        update_last_photo(user=user)

        # Update the assigned photo to this user and save the last label
        update_current_photo_user(user=user, next_photo=image_dict, working_dataset=working_dataset)

        # Send the next photo
        cv2.imwrite("temp.png", image)
        # Send the next photo
        TelegramBot.sendMessage(chat_id=int(user[0]),
                                text="What do you see in the following picture?")
        send_photo(TelegramBot=TelegramBot, user=user, image=image)
        os.remove("temp.png")
    else:
        for user in manager:
            TelegramBot.sendMessage(chat_id=user,
                                    text="Labelling task finished")
            TelegramBot.sendMessage(chat_id=user,
                                    text="I repeat, the labelling task has finished")


def start(TelegramBot, user):
    tutorial(TelegramBot, user)
    normal_execution(TelegramBot, user)


def send_help(TelegramBot, user):
    final_message, personal_msg = get_info(user[0])
    TelegramBot.sendMessage(chat_id=int(user[0]),
                            text=personal_msg)
    TelegramBot.sendMessage(chat_id=int(user[0]),
                            text=final_message)
    resend_last_image(TelegramBot, user)


def send_stats(TelegramBot, user):
    ranking = get_ranking()
    TelegramBot.sendMessage(chat_id=int(user[0]),
                            text="\U0001F3C6 Current ranking: \U0001F3C6")
    time.sleep(0.5)
    message = ""
    for index, player in enumerate(ranking, start=1):
        message = message + "\U0001F3C7\t{index} º. \t Player {player[0]} with {player[1]} labeled images\n".format(
            index=index, player=player)
    TelegramBot.sendMessage(chat_id=int(user[0]),
                            text=message)
    time.sleep(2)
    resend_last_image(TelegramBot, user)


def resend_last_image(TelegramBot, user):
    image = get_current_image(user_id=user[0])
    if image is not None:
        image = get_image(depth_path=image[1]["path_depth"])
        TelegramBot.sendMessage(chat_id=int(user[0]),
                                text="What do you see in the following picture?")
        send_photo(TelegramBot, user, image=image)
    else:
        normal_execution(TelegramBot, user)


def tutorial(TelegramBot, user):
    # There's a tutorial here and that's why all of this code...
    TelegramBot.sendMessage(chat_id=int(user[0]),
                            text="\U0001F411 \U0001F411 \U0001F411 \U0001F411 \U0001F411")
    time.sleep(1)
    TelegramBot.sendMessage(chat_id=int(user[0]),
                            text="We're trying to sort out a dataset to train a neural network \U0001F9E0 with a bunch of lamb's images.\U0001F411 \nWe only discriminate 4 options:")
    time.sleep(2)
    TelegramBot.sendMessage(chat_id=int(user[0]),
                            text=" \U0001F4BB These are the 4 options availables: \U0001F913")
    time.sleep(2)
    TelegramBot.sendMessage(chat_id=int(user[0]),
                            text="1. \U0001F411 A whole lamb. \U0001F411 \nThe image must contain the full animal, end to end; the head and the tail.")
    time.sleep(1)
    TelegramBot.sendMessage(chat_id=int(user[0]),
                            text="A few examples:")
    send_photo(TelegramBot, user=user,
               path=os.path.join(parent_folder, *"/dataset/examples/lamb_0.png".split("/")))
    time.sleep(1)
    send_photo(TelegramBot, user=user,
               path=os.path.join(parent_folder, *"/dataset/examples/lamb_1.png".split("/")))
    time.sleep(2)
    TelegramBot.sendMessage(chat_id=int(user[0]),
                            text="\U0001F411 ...We may send you a few grown sheeps \U0001F40F. If they are in the right position, it's also ok \U0001F44D.")
    time.sleep(2)
    TelegramBot.sendMessage(chat_id=int(user[0]),
                            text="A few examples:")
    time.sleep(1)
    send_photo(TelegramBot, user=user,
               path=os.path.join(parent_folder, *"/dataset/examples/sheep_0.png".split("/")))
    time.sleep(1)
    send_photo(TelegramBot, user=user,
               path=os.path.join(parent_folder, *"/dataset/examples/sheep_1.png".split("/")))

    time.sleep(2)
    TelegramBot.sendMessage(chat_id=int(user[0]),
                            text="2. \U0001F342 An empty space. \U0001F341 \nThere is no lamb \U0001F463 or anything like a little lamb. \U0001F342")
    time.sleep(1)
    TelegramBot.sendMessage(chat_id=int(user[0]),
                            text="A few examples:")
    send_photo(TelegramBot, user=user,
               path=os.path.join(parent_folder, *"/dataset/examples/empty_1.png".split("/")))
    time.sleep(1)
    send_photo(TelegramBot, user=user,
               path=os.path.join(parent_folder, *"/dataset/examples/empty_0.png".split("/")))
    time.sleep(2)
    TelegramBot.sendMessage(chat_id=int(user[0]),
                            text="3. \U0001F984 Wrong position.\n \U0001F42E There is more than one lamb in the picture, or there is only the head of our lamb \U0001F418, or the butt... but there is not a full body of a lamb. \U0001F984")
    TelegramBot.sendMessage(chat_id=int(user[0]),
                            text="A few examples:")
    time.sleep(1)
    send_photo(TelegramBot, user=user,
               path=os.path.join(parent_folder, *"/dataset/examples/dirty_head.png".split("/")))
    time.sleep(1)
    send_photo(TelegramBot, user=user,
               path=os.path.join(parent_folder, *"/dataset/examples/dirty_2lambs.png".split("/")))
    time.sleep(1)
    TelegramBot.sendMessage(chat_id=int(user[0]),
                            text="4. ...a fly.   \U0001F99F \nYes.\n \U0001F997 There are a lot of flies \U0001F4A9 in the farm; they use our cameras to everything they can possibly imagine \U0001F4A9. We're still working on it.\n \U0001F577 If you get an image that you can't interpretate \U0001F47B or just partially interpretate, please, \U0001F578 label it as a dirty image,\U0001F4A9 an error, a fly. \U0001F99F")
    time.sleep(1)
    TelegramBot.sendMessage(chat_id=int(user[0]),
                            text="A few examples:")
    time.sleep(1)
    send_photo(TelegramBot, user=user,
               path=os.path.join(parent_folder, *"/dataset/examples/dirty_lamb.png".split("/")))
    time.sleep(1)
    send_photo(TelegramBot, user=user, path=os.path.join(parent_folder, *"/dataset/examples/fly.png".split("/")))
    time.sleep(1)
    TelegramBot.sendMessage(chat_id=int(user[0]),
                            text="\U0001F411 That's it. Let's see the lambs! \U0001F411 \U0001F411")
    TelegramBot.sendMessage(chat_id=int(user[0]),
                            text="\U0001F411 \U0001F411 \U0001F411 \U0001F411 \U0001F411")

    time.sleep(3)


options = {"\U0001F411 A whole lamb": "lamb",
           "\U0001F342 Empty": "empty",
           "\U0001F984 Wrong position": "wrong",
           "\U0001F99F Error / flies": "fly"}

default_options = {"/start": start, "/stop": stop, "/restart": restart, "\U0001F937 I don't know": ignore,
                   "\U0001F914 Help": send_help, "/help": send_help, "/stats": send_stats}
