#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = "ipetrash"


import threading
import time


def run():
    i = 1

    # Бесконечный цикл
    while True:
        print(i)
        i += 1

        time.sleep(1)


if __name__ == "__main__":
    thread = threading.Thread(target=run, daemon=True)
    thread.start()

    # Wait
    thread.join(5)

    print("Quit!")
