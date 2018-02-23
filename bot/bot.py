#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Basic example for a bot that uses inline keyboards.

# This program is dedicated to the public domain under the CC0 license.
"""
import logging
import os.path

import requests
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)


def devices(bot, update):
    if os.path.isfile("devices.txt"):
        if os.path.getsize("devices.txt") > 0:
            with open('devices.txt') as devices_file:
                devices_list = devices_file.readlines()
                if len(devices_list) == 1:
                    name1 = devices_list[0].split(',')[0]
                    keyboard = [[InlineKeyboardButton(name1, callback_data=name1)],
                                [InlineKeyboardButton('Add device', callback_data='add'),
                                 InlineKeyboardButton('Cancel', callback_data='cancel')]]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    update.message.reply_text('Which device do you want to use?', reply_markup=reply_markup)

                elif len(devices_list) == 2:
                    name1 = devices_list[0].split(',')[0]
                    name2 = devices_list[1].split(',')[0]
                    keyboard = [[InlineKeyboardButton(name1, callback_data=name1),
                                 InlineKeyboardButton(name2, callback_data=name2)],
                                [InlineKeyboardButton('Add device', callback_data='add'),
                                 InlineKeyboardButton('Cancel', callback_data='cancel')]]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    update.message.reply_text('Which device do you want to use?', reply_markup=reply_markup)
        else:
            keyboard = [[InlineKeyboardButton('Add device', callback_data='add'),
                         InlineKeyboardButton('No', callback_data='cancel')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            update.message.reply_text('No device added, do you want to add one?', reply_markup=reply_markup)
    else:
        keyboard = [[InlineKeyboardButton('Add device', callback_data='add'),
                     InlineKeyboardButton('No', callback_data='cancel')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text('No device added, do you want to add one?', reply_markup=reply_markup)


def usage(bot, update, query):
    device = query.data
    keyboard = [[InlineKeyboardButton("Toggle", callback_data='toggle/' + device),
                 InlineKeyboardButton("Info", callback_data='info/' + device)],
                [InlineKeyboardButton('Remove device', callback_data='remove/' + device)]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    bot.edit_message_text('What do you want to do with ' + device + '?', reply_markup=reply_markup,
                          chat_id=query.message.chat_id,
                          message_id=query.message.message_id)


def removedevice(bot, update):
    device = update.message.text[8::]
    devices_file = open("devices.txt", 'r')
    lines = devices_file.readlines()
    devices_file.close()
    devices_file = open("devices.txt", 'w')
    for line in lines:
        if device not in line:
            devices_file.write(line)
        else:
            update.message.reply_text('Device (' + line + ') removed!')


def adddevice(bot, update):
    device = update.message.text[5::]
    with open("devices.txt", 'a') as devices_file:
        devices_file.write(device + '\n')
        update.message.reply_text('Device (' + device + ') added!')


def action(device, request):
    with open("devices.txt") as devices_file:
        for line in devices_file:
            if device in line:
                ip = line.split(',')[1][1:-1]
                link = "http://" + ip + "/cm?cmnd=Power"
                if request == 'toggle':
                    link += "%20TOGGLE"
                f = requests.get(link)
                return f.text[10:-2].lower()


def button(bot, update):
    query = update.callback_query

    if 'toggle' in query.data or 'info' in query.data:
        text = query.data
        device = text.split('/')[1]
        request = text.split('/')[0]
        bot.edit_message_text(text=device + " is " + action(device, request) + ".",
                              chat_id=query.message.chat_id,
                              message_id=query.message.message_id)
    elif query.data == 'add':
        bot.edit_message_text(text='Add a device like this: "/add device_name, device_ip".',
                              chat_id=query.message.chat_id,
                              message_id=query.message.message_id)
    elif query.data == 'cancel':
        bot.edit_message_text(text='Command canceled.',
                              chat_id=query.message.chat_id,
                              message_id=query.message.message_id)
    elif 'remove' in query.data:
        device = query.data.split('/')[1]
        devices_file = open("devices.txt", 'r')
        lines = devices_file.readlines()
        devices_file.close()
        devices_file = open("devices.txt", 'w')
        for line in lines:
            if device not in line:
                devices_file.write(line)

        bot.edit_message_text(text='Device removed.',
                              chat_id=query.message.chat_id,
                              message_id=query.message.message_id)
    else:
        usage(bot, update, query)


def help(bot, update):
    update.message.reply_text("/devices")


def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)


def main():
    # Create the Updater and pass it your bot's token.
    print "Bot started..."

    updater = Updater(token())

    updater.dispatcher.add_handler(CommandHandler('devices', devices))
    updater.dispatcher.add_handler(CommandHandler('add', adddevice))
    updater.dispatcher.add_handler(CommandHandler('remove', removedevice))
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
        data = filter(None, (line.rstrip() for line in tokenfile))[0]
        return data


if __name__ == '__main__':
    main()
