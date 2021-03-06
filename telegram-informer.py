#!/usr/bin/python3
# -*- coding: utf-8 -*-
#    telegram-informer.py - the displaying interface for Telegram.
#    Copyright (C) 2016 Danya Generalov
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters,\
    CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Bot
import logging
import json
import threading
import os
import sys

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)

logger = logging.getLogger(__name__)

AWAIT_CONFIRMATION, AWAIT_INPUT = range(2)
YES, NO = ("Yes", "No")
state = dict()
context = dict()
try:
    values = eval(open("./users.json").read())
except:
    values = list()


def entered_value(bot, update):
    chat_id = update.message.chat_id
    user_id = update.message.from_user.id
    chat_state = state.get(user_id, AWAIT_INPUT)

    # Check if we are waiting for input
    if chat_state == AWAIT_INPUT:
        state[user_id] = AWAIT_CONFIRMATION

        # Save the user id and the answer to context
        context[user_id] = update.message.text
        reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton(YES, callback_data=YES),
             InlineKeyboardButton(NO, callback_data=NO)]])
        bot.sendMessage(chat_id, text="Are you sure?",
                        reply_markup=reply_markup)


def confirm_value(bot, update):
    query = update.callback_query
    chat_id = query.message.chat_id
    user_id = query.from_user.id
    text = query.data
    user_state = state.get(user_id, AWAIT_INPUT)

    # Check if we are waiting for confirmation and the right user answered
    if user_state == AWAIT_CONFIRMATION:
        del state[user_id]
        del context[user_id]
        if text == YES:
            if values.count(user_id) > 0:
                txt = "Unregistered!"
                txt_long = "You are no longer registered."
                values.remove(user_id)
            else:
                txt = "Registered!"
                txt_long = "You are now registered.  To recieve updates, please do not close this chat window and do not push the `Stop Bot` button."
                values.append(user_id)
        else:
            txt = "Not changed!"
            if user_id in values:
                txt_long = "You are still registered."
            else:
                txt_long = "You are still unregistered."
        bot.answerCallbackQuery(query.id, text=txt)

        bot.editMessageText(text=txt_long,
                            chat_id=chat_id,
                            message_id=query.message.message_id)


def start(bot, update):
    bot.sendMessage(update.message.chat_id,
                    text="Welcome to Yandex.Probki notification service. Select /help for help.")


def help(bot, update):
    bot.sendMessage(update.message.chat_id, text="""/help - command list
/registration - toggle notifications
/status - get current traffic congestion""")


def error(bot, update, error):
    logger.warn('Update "%s" caused error "%s"' % (update, error))


def saver():
    import time
    while 1:
        open("./users.json", "w").write(str(values))
        time.sleep(10)
saver_thread = threading.Thread(target=saver, name="saver")
saver_thread.start()
global cong
cong = 0


def loader():
    import time
    global cong
    while 1:
        os.popen("./acquirer.py").read()
        try:
            if os.name == "os2" or os.name == "posix":  # unix
                tmp_path = "/tmp"
            elif os.name == "nt":  # windows
                tmp_path = os.path.join(os.path.splitdrive(sys.executable)[0],
                                        "windows", "temp")
            else:  # some other weird system like riscos
                raise NotImplementedError("Unknown system type: "+os.name)

            cong = int(open(tmp_path+os.sep+".last_traffic").read().split(
                ":")[1].split(",")[1])
        except:
            pass
        time.sleep(60)
loader_thread = threading.Thread(target=loader, name="loader")
loader_thread.start()


def sender():
    sent = False
    bot = Bot(token=json.load(open("config.json")["token"]))
    import time
    global cong
    global send_now
    while 1:
        if time.localtime(time.time())[3] == 16 and \
          time.localtime(time.time())[4] == 59 and \
          time.localtime(time.time())[5] == 59:
            sent = False
        if send_now or time.localtime(time.time())[3] >= 17 and cong < 7 and not sent:
            sent = True
            for i in values:
                try:
                    bot.sendMessage(i, text="Your registered update has occurred: the level of traffic congestion is now lower than 7.")
                except:
                    print("error on", str(i))
        time.sleep(1)
sender_thread = threading.Thread(target=sender, name="sender")
sender_thread.start()


def status(bot, update):
    global cong
    bot.sendMessage(update.message.chat_id,
                    text="Current traffic status: "+str(cong)+"/10")
    bot.sendPhoto(update.message.chat_id, json.load(open("./config.json"))["url"])
    # query = update.callback_query
    if update.to_dict()["message"]["from"]["id"] not in values:
            bot.sendMessage(update.to_dict()["message"]["chat"]["id"],
                            text="Don't want to check this value every so often? Sign up for notifications!")
            bot.sendMessage(update.to_dict()["message"]["chat"]["id"],
                            text="This bot will send you a message after 17:00 when the level of traffic congestion will be below 7.")
            bot.sendMessage(update.to_dict()["message"]["chat"]["id"],
                            text="Select the /registration command to register for updates.")


def main():
    # Create the EventHandler and pass it your bot's token.
    updater = Updater(json.load(open("config.json")["token"]))

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("registration", entered_value))
    dp.add_handler(CommandHandler("status", status))
    # on noncommand i.e message - echo the message on Telegram
    dp.add_handler(MessageHandler([Filters.text], entered_value))
    updater.dispatcher.add_handler(CallbackQueryHandler(confirm_value))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until the you presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
