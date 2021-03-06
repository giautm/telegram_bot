#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Modified example of inline-keyboard bot.

# This program is dedicated to the public domain under the CC0 license.
"""
import logging
import os.path
import subprocess

import requests
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)


def mainmenu(bot, update):
    if os.path.isfile("devices.txt"):
        if os.path.getsize("devices.txt") > 0:
            with open('devices.txt') as devices_file:
                devices_list = devices_file.readlines()
                keyboard = []
                for line in devices_list:
                    device = line.split(',')[0]
                    keyboard.append([InlineKeyboardButton(device, callback_data=device)], )
                keyboard.append([InlineKeyboardButton('Add device', callback_data='add'),
                                 InlineKeyboardButton('Cancel', callback_data='cancel')])
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


def toggle(bot, update):
    with open('devices.txt') as devices_file:
        devices_list = devices_file.readlines()
        keyboard = []
        for line in devices_list:
            device = line.split(',')[0]
            keyboard.append([InlineKeyboardButton(device, callback_data='toggle/' + device)], )
        keyboard.append([InlineKeyboardButton('Toggle all', callback_data='toggleall')])
        keyboard.append([InlineKeyboardButton('Cancel', callback_data='cancel')])
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text('Which device do you want to toggle?', reply_markup=reply_markup)


def info(bot, update):
    with open('devices.txt') as devices_file:
        devices_list = devices_file.readlines()
        message = ''
        for line in devices_list:
            device = line.split(',')[0]
            message += device + " is " + action(device, 'info') + ".\n"
        update.message.reply_text(message)


def usage(bot, update, query):
    device = query.data
    keyboard = [[InlineKeyboardButton("Toggle", callback_data='toggle/' + device),
                 InlineKeyboardButton("Info", callback_data='info/' + device)],
                [InlineKeyboardButton('Remove device', callback_data='remove/' + device)],
                [InlineKeyboardButton('Cancel', callback_data='cancel')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    bot.edit_message_text('What do you want to do with ' + device + '?', reply_markup=reply_markup,
                          chat_id=query.message.chat_id,
                          message_id=query.message.message_id)


def removedevice(bot, update):
    if os.path.isfile("devices.txt"):
        if os.path.getsize("devices.txt") > 0:
            with open('devices.txt') as devices_file:
                devices_list = devices_file.readlines()
                keyboard = []
                for line in devices_list:
                    device = line.split(',')[0]
                    keyboard.append([InlineKeyboardButton(device, callback_data='remove/' + device)], )
                keyboard.append([InlineKeyboardButton('Cancel', callback_data='cancel')])
                reply_markup = InlineKeyboardMarkup(keyboard)
                update.message.reply_text('What device do you want to remove?', reply_markup=reply_markup)
    else:
        keyboard = [[InlineKeyboardButton('Add device', callback_data='add'),
                     InlineKeyboardButton('No', callback_data='cancel')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text('No device added, do you want to add one?', reply_markup=reply_markup)


def adddevice(bot, update):
    device = update.message.text[5::]
    if len(device.split(',')) < 2:
        update.message.reply_text('Command not used properly. Use /help to see the commands.')
    else:
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
        if query.data == 'toggleall':
            with open('devices.txt') as devices_file:
                devices_list = devices_file.readlines()
                message = ''
                for line in devices_list:
                    device = line.split(',')[0]
                    message += device + " is " + action(device, 'toggle') + ".\n"
                bot.edit_message_text(text=message,
                                      chat_id=query.message.chat_id,
                                      message_id=query.message.message_id)
        else:
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
            else:
                bot.edit_message_text(text=('Device (' + line.split('\n')[0] + ') removed!'),
                                      chat_id=query.message.chat_id,
                                      message_id=query.message.message_id)
    else:
        usage(bot, update, query)


def wake(bot, update):
    if os.path.isfile('wake.txt'):
        with open('wake.txt') as wake_file:
            address = filter(None, (line.rstrip() for line in wake_file))[0]
            fnull = open(os.devnull, 'w')
            retcode = subprocess.call(['wakeonlan', address], stdout=fnull, stderr=subprocess.STDOUT)
            update.message.reply_text('Wake executed.')
    else:
        update.message.reply_text('No device to wake.')


def addwake(bot, update):
    if os.path.isfile('wake.txt'):
        update.message.reply_text('Wake already added!')
    else:
        address = update.message.text[9::]
        with open("wake.txt", 'a') as devices_file:
            devices_file.write(address + '\n')
            update.message.reply_text('Wake (' + address + ') added!')


def removewake(bot, update):
    if os.path.isfile('wake.txt'):
        os.remove('wake.txt')
        update.message.reply_text('Wake removed!')


def help(bot, update):
    update.message.reply_text('Available commands:'
                              + '\n' + '/main (to get to the main menu)'
                              + '\n' + '/toggle (to toggle a device)'
                              + '\n' + '/info (to get information about all devices)'
                              + '\n' + '/add device_name, device_ip (to add a device)'
                              + '\n' + '/remove (to remove a device)'
                              + '\n' + '/wake (to wake the pc)'
                              + '\n' + '/addwake (to add the pc)'
                              + '\n' + '/removewake (to remove the pc)')


def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)


def main():
    # Create the Updater and pass it your bot's token.
    print "Bot started..."

    updater = Updater(token())

    updater.dispatcher.add_handler(CommandHandler('main', mainmenu))
    updater.dispatcher.add_handler(CommandHandler('add', adddevice))
    updater.dispatcher.add_handler(CommandHandler('remove', removedevice))
    updater.dispatcher.add_handler(CommandHandler('toggle', toggle))
    updater.dispatcher.add_handler(CommandHandler('info', info))

    updater.dispatcher.add_handler(CommandHandler('wake', wake))
    updater.dispatcher.add_handler(CommandHandler('addwake', addwake))
    updater.dispatcher.add_handler(CommandHandler('removewake', removewake))

    updater.dispatcher.add_handler(CallbackQueryHandler(button))
    updater.dispatcher.add_handler(CommandHandler('help', help))
    updater.dispatcher.add_handler(CommandHandler('start', help))
    updater.dispatcher.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until the user presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT
    updater.idle()


def token():
    if os.path.isfile('/home/pi/token.txt'):
        with open('/home/pi/token.txt', 'r') as tokenfile:
            data = filter(None, (line.rstrip() for line in tokenfile))[0]
            return data


if __name__ == '__main__':
    main()
