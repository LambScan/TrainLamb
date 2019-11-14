import time
import telepot
from telepot.loop import MessageLoop
from features import upload_info, start, stop, restart, ignore
from FileManager import parent_folder
import os

__TOKEN__ = None


def __get_token__():
    with open(os.path.join(parent_folder, "etc", "config")) as f:
        __TOKEN__ = f.readline().replace("\n", "")
    return str(__TOKEN__)


options = {"\U0001F411 One complete lamb \U0001F411": "lamb",
           "\U0001F342 Empty \U0001F342": "empty",
           "\U0001F984 Not exactly one complete lamb \U0001F984": "wrong",
           "\U0001F99F Error / Dirty / A fly \U0001F99F": "fly"}

default_options = {"/start": start, "/stop": stop, "/restart": restart, "\U0001F937 I don't know \U0001F937": ignore,
                   "\U0001F195 Next one \U0001F195": ignore}


def on_chat_message(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)

    if content_type == "text":
        text = msg["text"]
        if text in default_options:
            default_options[text](my_bot, chat_id)
        # if text == "/start":
        #     start(my_bot, chat_id)
        # elif text == "/stop":
        #     stop(my_bot, chat_id)
        # elif text == "/restart":
        #     restart(my_bot, chat_id)
        # elif "I don't know" in text or "Next one" in text:
        #     ignore(my_bot, chat_id)
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
