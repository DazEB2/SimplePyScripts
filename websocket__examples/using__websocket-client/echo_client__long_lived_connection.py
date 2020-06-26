#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'ipetrash'


# SOURCE: https://github.com/websocket-client/websocket-client#long-lived-connection


try:
    import thread
except ImportError:
    import _thread as thread
import time


# pip install websocket-client
import websocket


def on_open(ws):
    print(f'[on_open]')

    def run(*args):
        for i in range(3):
            time.sleep(1)
            ws.send(f"Hello {i}")

        time.sleep(1)
        ws.close()

        print("thread terminating...")

    thread.start_new_thread(run, ())


def on_message(ws, message):
    print(f'[on_message] {message}')


def on_error(ws, error):
    print(f'[on_error] {error}')


def on_close(ws):
    print(f'[on_close]')


if __name__ == "__main__":
    # From http://websocket.org/echo.html
    url = 'wss://echo.websocket.org'

    websocket.enableTrace(True)
    ws = websocket.WebSocketApp(
        url,
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
    )
    ws.run_forever()
