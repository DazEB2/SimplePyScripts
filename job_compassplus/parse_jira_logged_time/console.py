#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = "ipetrash"


import re
import xml.etree.ElementTree as ET
import sys

from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, date, timezone

from config import ROOT_DIR, USERNAME, MAX_RESULTS, JIRA_HOST

sys.path.append(str(ROOT_DIR))
from root_common import session

sys.path.append(str(ROOT_DIR.parent))
from logged_human_time_to_seconds import logged_human_time_to_seconds
from seconds_to_str import seconds_to_str


URL: str = (
    f"{JIRA_HOST}/activity?maxResults={MAX_RESULTS}"
    f"&streams=user+IS+{USERNAME}&os_authType=basic&title=undefined"
)


@dataclass
class Activity:
    entry_dt: datetime
    jira_id: str
    jira_title: str
    logged_human_time: str | None = None
    logged_seconds: int | None = None

    def is_logged(self) -> bool:
        return bool(self.logged_seconds)


# SOURCE: https://stackoverflow.com/a/13287083/5909792
def utc_to_local(utc_dt: datetime) -> datetime:
    return utc_dt.replace(tzinfo=timezone.utc).astimezone(tz=None)


def get_rss_jira_log() -> bytes:
    rs = session.get(URL)
    rs.raise_for_status()
    return rs.content


def get_date_by_activities(root) -> dict[date, list[Activity]]:
    ns = {
        "": "http://www.w3.org/2005/Atom",
        "activity": "http://activitystrea.ms/spec/1.0/",
    }

    def _get_text(el, xpath: str) -> str:
        return el.find(xpath, namespaces=ns).text.strip()

    result: dict[date, list[Activity]] = defaultdict(list)

    pattern_logged = re.compile("logged '(.+?)'", flags=re.IGNORECASE)

    for entry in root.findall("./entry", namespaces=ns):
        # Ищем в <entry> строку с логированием
        if m := pattern_logged.search("".join(entry.itertext())):
            logged_human_time = m.group(1)
            logged_seconds = logged_human_time_to_seconds(logged_human_time)
        else:
            logged_human_time = logged_seconds = None

        try:
            jira_id = _get_text(entry, "./activity:object/title")
            jira_title = _get_text(entry, "./activity:object/summary")
        except:
            jira_id = _get_text(entry, "./activity:target/title")
            jira_title = _get_text(entry, "./activity:target/summary")

        # Переменная entry_dt имеет время в UTC, и желательно его привести в локальное время
        entry_dt = datetime.strptime(
            _get_text(entry, "./published"),
            "%Y-%m-%dT%H:%M:%S.%fZ",
        )
        entry_dt = utc_to_local(entry_dt)
        entry_date = entry_dt.date()

        result[entry_date].append(
            Activity(
                entry_dt=entry_dt,
                jira_id=jira_id,
                jira_title=jira_title,
                logged_human_time=logged_human_time,
                logged_seconds=logged_seconds,
            )
        )

    return result


def parse_date_by_activities(xml_data: bytes) -> dict[date, list[Activity]]:
    root = ET.fromstring(xml_data)
    return get_date_by_activities(root)


def get_logged_total_seconds(activities: list[Activity]) -> int:
    return sum(obj.logged_seconds for obj in activities if obj.is_logged())


if __name__ == "__main__":
    print(URL)

    xml_data = get_rss_jira_log()
    print(len(xml_data), repr(xml_data[:50]))
    print()

    # Структура документа - xml
    date_by_activities: dict[date, list[Activity]] = parse_date_by_activities(xml_data)
    # print(date_by_activities)
    # print()

    # Для красоты выводим результат в табличном виде
    lines = [
        ("DATE", "LOGGED", "SECONDS", "ACTIVITIES"),
    ]
    for entry_date, activities in sorted(
        date_by_activities.items(), key=lambda x: x[0], reverse=True
    ):
        total_seconds: int = get_logged_total_seconds(activities)
        total_seconds_str: str = seconds_to_str(total_seconds)

        date_str: str = entry_date.strftime("%d/%m/%Y")
        lines.append((date_str, total_seconds_str, total_seconds, len(activities)))

    # Список строк станет списком столбцов, у каждого столбца подсчитается максимальная длина
    max_len_columns = [max(map(len, map(str, col))) for col in zip(*lines)]

    # Создание строки форматирования: [30, 14, 5] -> "{:<30} | {:<14} | {:<5}"
    my_table_format = " | ".join("{:<%s}" % max_len for max_len in max_len_columns)

    for line in lines:
        print(my_table_format.format(*line))
