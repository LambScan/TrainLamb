import os
import time
import telepot
from telepot.loop import MessageLoop
from FileManager import parent_folder
from features import upload_info, start, stop, restart, ignore, options, default_options

__TOKEN__ = None


def __get_token__():
    with open(os.path.join(parent_folder, "etc", "config")) as f:
        __TOKEN__ = f.readline().replace("\n", "")
    return str(__TOKEN__)


def on_chat_message(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)
    # user = (chat_id, msg["from"]["first_name"], msg["from"]["username"])
    if content_type == "text":
        text = msg["text"]
        if text in default_options:
            default_options[text](my_bot, chat_id)
        elif text in options:
            upload_info(my_bot, chat_id, options[text])
        else:
            print("A message with no label came. We should be sending a prefedined message...")
            my_bot.sendMessage(chat_id=chat_id, text="Only predefined options are supported by this little lamb.")

    else:
        my_bot.sendMessage(chat_id=chat_id, text="Non text messages ain't supported by this poor little lamb.")


if __name__ == '__main__':
    my_bot = telepot.Bot(__get_token__())
    MessageLoop(my_bot, {'chat': on_chat_message}).run_as_thread()
    print('Listening ...')

    while 1:
        time.sleep(10)
