#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'ipetrash'


import keyboard
keyboard.add_hotkey('shift', lambda: keyboard.write('on'))
keyboard.add_hotkey('shift', lambda: keyboard.write('off'), trigger_on_release=True)

# Block forever.
keyboard.wait()
