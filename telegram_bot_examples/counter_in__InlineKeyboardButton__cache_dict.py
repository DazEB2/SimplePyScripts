#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'ipetrash'


import os
from typing import Dict
from pathlib import Path

# pip install python-telegram-bot
from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup
)
from telegram.ext import Updater, MessageHandler, CommandHandler, Filters, CallbackContext, CallbackQueryHandler
from telegram.ext.dispatcher import run_async

import config
from common import get_logger, log_func


log = get_logger(str(Path(__file__)) + '.log')


DATA_TEMPLATE = {
    'number_1': 0,
    'number_2': 0,
    'number_3': 0,
}

# chat_id -> message_id -> DATA_TEMPLATE
CACHE_NUMBERS: Dict[int, Dict[int, Dict[str, int]]] = dict()


def get_reply_markup(data: Dict[str, int]) -> InlineKeyboardMarkup:
    keyboard = [[
        InlineKeyboardButton(str(value), callback_data=data)
        for data, value in data.items()
    ]]
    return InlineKeyboardMarkup(keyboard)


@run_async
@log_func(log)
def on_start(update: Update, context: CallbackContext):
    update.message.reply_text(
        f'Введите что-нибудь'
    )


@run_async
@log_func(log)
def on_request(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    message_id = update.message.message_id

    if chat_id not in CACHE_NUMBERS:
        CACHE_NUMBERS[chat_id] = dict()
    if message_id not in CACHE_NUMBERS[chat_id]:
        CACHE_NUMBERS[chat_id][message_id] = DATA_TEMPLATE.copy()

    data = CACHE_NUMBERS[chat_id][message_id]

    update.message.reply_text(
        'Ok',
        reply_markup=get_reply_markup(data)
    )


@run_async
@log_func(log)
def on_callback_query(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    chat_id = query.message.chat_id
    message_id = query.message.message_id

    # Restore from inline keyboard of message
    if chat_id not in CACHE_NUMBERS:
        CACHE_NUMBERS[chat_id] = dict()

    if message_id not in CACHE_NUMBERS[chat_id]:
        inline_keyboard = query.message.reply_markup.inline_keyboard
        data = dict()
        for rows in inline_keyboard:
            for x in rows:
                data[x.callback_data] = int(x.text)
        CACHE_NUMBERS[chat_id][message_id] = data

    data = CACHE_NUMBERS[chat_id][message_id]
    data[query.data] += 1

    query.message.edit_reply_markup(
        reply_markup=get_reply_markup(data)
    )


def error_callback(update: Update, context: CallbackContext):
    log.exception('Error: %s\nUpdate: %s', context.error, update)
    update.message.reply_text(config.ERROR_TEXT)


def main():
    cpu_count = os.cpu_count()
    workers = cpu_count
    log.debug('System: CPU_COUNT=%s, WORKERS=%s', cpu_count, workers)

    log.debug('Start')

    # Create the EventHandler and pass it your bot's token.
    updater = Updater(
        config.TOKEN,
        workers=workers,
        use_context=True
    )

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    dp.add_handler(CommandHandler('start', on_start))
    dp.add_handler(MessageHandler(Filters.text, on_request))
    dp.add_handler(CallbackQueryHandler(on_callback_query))

    # log all errors
    dp.add_error_handler(error_callback)

    # Start the Bot
    updater.start_polling()

    # Run the bot until the you presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()

    log.debug('Finish')


if __name__ == '__main__':
    while True:
        try:
            main()
        except:
            log.exception('')
