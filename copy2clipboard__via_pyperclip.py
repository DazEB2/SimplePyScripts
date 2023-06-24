#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = "ipetrash"


import pyperclip


def to(text: str):
    pyperclip.copy(text)
    pyperclip.paste()


if __name__ == "__main__":
    import sys
    import os

    if len(sys.argv) > 1:
        text = " ".join(sys.argv[1:])
        print('Text: "{}"'.format(text))
        to(text)
    else:
        file_name = os.path.basename(sys.argv[0])
        print("usage: {} [-h] text".format(file_name))
