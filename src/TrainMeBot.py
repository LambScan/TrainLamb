import time
import telepot
from telepot.loop import MessageLoop
from features import upload_info, start, stop, restart, ignore

__TOKEN__ = None


def __get_token__():
    with open("../etc/config") as f:
        __TOKEN__ = f.readline().replace("\n", "")
    return str(__TOKEN__)


options = {"Lamb": "lamb",
           "Empty": "empty",
           "Error": "error",
           "There's a fly\nor something": "fly"}


def on_chat_message(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)

    if content_type == "text":
        text = msg["text"]
        if text == "/start":
            start(my_bot, chat_id)
        elif text == "/stop":
            stop(my_bot, chat_id)
        elif text == "/restart":
            restart(my_bot, chat_id)
        elif text in ("I don't know", "Next one"):
            ignore(my_bot, chat_id)
        elif text in options:
            upload_info(my_bot, chat_id, options[text])
    else:
        my_bot.sendMessage(chat_id=chat_id, text="Non text messages ain't supported by this poor little lamb.")


if __name__ == '__main__':
    my_bot = telepot.Bot(__get_token__())
    MessageLoop(my_bot, {'chat': on_chat_message}).run_as_thread()
    print('Listening ...')

    while 1:
        time.sleep(10)
