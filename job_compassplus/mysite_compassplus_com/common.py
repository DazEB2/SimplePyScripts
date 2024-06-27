#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = "ipetrash"


import sys
from pathlib import Path

DIR = Path(__file__).resolve().parent
ROOT_DIR = DIR.parent

sys.path.append(str(ROOT_DIR))
from site_common import do_get


URL = "https://mysite.compassplus.com/Person.aspx?accountname={}"


if __name__ == "__main__":
    rs = do_get("https://mysite.compassplus.com:443/Person.aspx?accountname=CP%5Cipetrash")
    print(rs)
