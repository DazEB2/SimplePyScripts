#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'ipetrash'


import json
from dataclasses import dataclass, asdict
from typing import List, Union
from pathlib import Path

from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import MoveTargetOutOfBoundsException


# SOURCE: https://github.com/gil9red/SimplePyScripts/blob/f0403620f7948306ad9e34a373f2aabc0237fb2a/seconds_to_str.py
def seconds_to_str(seconds: int) -> str:
    hh, mm = divmod(seconds, 3600)
    mm, ss = divmod(mm, 60)
    return "%02d:%02d:%02d" % (hh, mm, ss)


@dataclass
class Track:
    title: str
    artists: str
    length: str
    is_available: bool

    def get_full_title(self) -> str:
        return f'{self.artists}: {self.title}'

    def get_seconds(self) -> int:
        """
        3:30 -> 3 * 60 + 30 -> 210
        :return: seconds
        """
        if not self.length:
            return 0

        parts = self.length.split(':')
        if len(parts) != 2:
            return 0
        return int(parts[0]) * 60 + int(parts[1])


def print_statistic(tracks: List[Track]):
    print_fmt = "{:%s}. {}" % len(str(len(tracks)))

    unavailable_tracks = []
    total_secs = 0

    for track in tracks:
        if not track.is_available:
            unavailable_tracks.append(track)

        total_secs += track.get_seconds()

    print('Total tracks:', len(tracks))
    print(f'Total length: {seconds_to_str(total_secs)} ({total_secs} secs)')
    print()

    print(f'Unavailable tracks ({len(unavailable_tracks)}):')
    for i, track in enumerate(unavailable_tracks, 1):
        print(print_fmt.format(i, track.get_full_title()))


def dump(tracks: List[Track], file_name: Union[str, Path]):
    json.dump(
        tracks,
        open(file_name, 'w', encoding='utf-8'),
        ensure_ascii=False,
        indent=4,
        default=lambda obj: asdict(obj) if isinstance(obj, Track) else obj
    )


def is_displayed_in_viewport(driver, element) -> bool:
    try:
        ActionChains(driver).move_to_element(element).perform()
        return True
    except MoveTargetOutOfBoundsException:
        return False
