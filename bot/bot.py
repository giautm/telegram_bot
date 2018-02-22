#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Basic example for a bot that uses inline keyboards.

# This program is dedicated to the public domain under the CC0 license.
"""
import logging

import requests
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)


def lampe(bot, update):
    keyboard = [[InlineKeyboardButton("Toggle", callback_data='toggle'),
                 InlineKeyboardButton("Info", callback_data='info')]]

    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text('Please choose:', reply_markup=reply_markup)


def link(request):
    link = "http://192.168.2.61/cm?cmnd=Power"
    if request == 'toggle':
        link += "%20TOGGLE"
    f = requests.get(link)
    return f.text[10:-2].lower()


def button(bot, update):
    query = update.callback_query

    bot.edit_message_text(text="Lampe is " + link(query.data) + ".",
                          chat_id=query.message.chat_id,
                          message_id=query.message.message_id)


def help(bot, update):
    update.message.reply_text("/lampe")


def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)


def main():
    # Create the Updater and pass it your bot's token.
    updater = Updater(token())

    updater.dispatcher.add_handler(CommandHandler('lampe', lampe))
    updater.dispatcher.add_handler(CallbackQueryHandler(button))
    updater.dispatcher.add_handler(CommandHandler('help', help))
    updater.dispatcher.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until the user presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT
    updater.idle()


def token():
    with open('/home/pi/token.txt', 'r') as tokenfile:
        data = tokenfile.read()
        data = data.split('/n')[0]
        print data
        return data


if __name__ == '__main__':
    main()
