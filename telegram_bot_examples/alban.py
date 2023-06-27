#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = "ipetrash"


import sys

# pip install python-telegram-bot
from telegram import Update
from telegram.ext import MessageHandler, CommandHandler, Filters, CallbackContext

from common import get_logger, log_func, start_bot, run_main

sys.path.append("../html_parsing")
from олбанский_alban import get_alban


log = get_logger(__file__)


@log_func(log)
def on_start(update: Update, _: CallbackContext):
    update.effective_message.reply_text("Write something")


@log_func(log)
def on_request(update: Update, _: CallbackContext):
    message = update.effective_message

    message.reply_text(get_alban(message.text))


def main():
    handlers = [
        CommandHandler("start", on_start),
        MessageHandler(Filters.text, on_request),
    ]
    start_bot(log, handlers)


if __name__ == "__main__":
    run_main(main, log)
