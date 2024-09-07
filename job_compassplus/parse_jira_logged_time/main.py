#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = "ipetrash"


import re
import xml.etree.ElementTree as ET
import sys

from collections import defaultdict
from datetime import datetime, timezone

from config import ROOT_DIR, USERNAME, MAX_RESULTS

sys.path.append(str(ROOT_DIR))
from root_common import session

sys.path.append(str(ROOT_DIR.parent))
from logged_human_time_to_seconds import logged_human_time_to_seconds
from seconds_to_str import seconds_to_str


URL: str = (
    f"https://helpdesk.compassluxe.com/activity?maxResults={MAX_RESULTS}"
    f"&streams=user+IS+{USERNAME}&os_authType=basic&title=undefined"
)


# SOURCE: https://stackoverflow.com/a/13287083/5909792
def utc_to_local(utc_dt: datetime) -> datetime:
    return utc_dt.replace(tzinfo=timezone.utc).astimezone(tz=None)


def get_rss_jira_log() -> bytes:
    rs = session.get(URL)
    rs.raise_for_status()
    return rs.content


def get_logged_dict(root) -> dict[str, list[dict]]:
    logged_dict = defaultdict(list)

    ns = {
        "": "http://www.w3.org/2005/Atom",
        "activity": "http://activitystrea.ms/spec/1.0/",
    }

    for entry in root.findall("./entry", namespaces=ns):
        # Ищем в <entry> строку с логированием
        match = re.search("logged '(.+?)'", "".join(entry.itertext()), flags=re.IGNORECASE)
        if not match:
            continue

        logged_human_time = match.group(1)
        logged_seconds = logged_human_time_to_seconds(logged_human_time)

        jira_id = entry.find("./activity:object/title", namespaces=ns).text.strip()
        jira_title = entry.find("./activity:object/summary", namespaces=ns).text.strip()

        entry_dt = datetime.strptime(
            entry.find("./published", namespaces=ns).text,
            "%Y-%m-%dT%H:%M:%S.%fZ",
        )

        # Переменная entry_dt имеет время в UTC, и желательно его привести в локальное время
        entry_dt = utc_to_local(entry_dt)

        entry_date = entry_dt.date()
        date_str = entry_date.strftime("%d/%m/%Y")

        logged_dict[date_str].append({
            "date_time": entry_dt.strftime("%d/%m/%Y %H:%M:%S"),
            "date": entry_dt.strftime("%d/%m/%Y"),
            "time": entry_dt.strftime("%H:%M:%S"),
            "logged_human_time": logged_human_time,
            "logged_seconds": logged_seconds,
            "jira_id": jira_id,
            "jira_title": jira_title,
        })

    return logged_dict


def parse_logged_dict(xml_data: bytes) -> dict[str, list[dict]]:
    root = ET.fromstring(xml_data)
    return get_logged_dict(root)


def get_sorted_logged(
    date_str_by_logged_list: dict, reverse=True
) -> list[tuple[str, list[dict]]]:
    sorted_items = date_str_by_logged_list.items()
    sorted_items = sorted(
        sorted_items, key=lambda x: datetime.strptime(x[0], "%d/%m/%Y"), reverse=reverse
    )

    return list(sorted_items)


def get_logged_list_by_now_utc_date(
    date_str_by_entry_logged_list: dict[str, list[dict]]
) -> list[dict]:
    current_utc_date_str = datetime.utcnow().strftime("%d/%m/%Y")
    return date_str_by_entry_logged_list.get(current_utc_date_str, [])


def get_logged_total_seconds(entry_logged_list: list[dict]) -> int:
    return sum(entry["logged_seconds"] for entry in entry_logged_list)


if __name__ == "__main__":
    print(URL)

    xml_data = get_rss_jira_log()
    print(len(xml_data), repr(xml_data[:50]))

    # open('rs.xml', 'wb').write(xml_data)
    # xml_data = open('rs.xml', 'rb').read()

    # Структура документа -- xml
    logged_dict = parse_logged_dict(xml_data)
    print(logged_dict)

    import json
    print(json.dumps(logged_dict, indent=4, ensure_ascii=False))
    print()

    logged_list = get_logged_list_by_now_utc_date(logged_dict)
    logged_total_seconds = get_logged_total_seconds(logged_list)
    print("entry_logged_list:", logged_list)
    print("today seconds:", logged_total_seconds)
    print("today time:", seconds_to_str(logged_total_seconds))
    print()

    # Для красоты выводим результат в табличном виде
    lines = []
    for date_str, logged_list in get_sorted_logged(logged_dict):
        total_seconds = get_logged_total_seconds(logged_list)
        lines.append((date_str, total_seconds, seconds_to_str(total_seconds)))

    # Список строк станет списком столбцов, у каждого столбца подсчитается максимальная длина
    max_len_columns = [max(map(len, map(str, col))) for col in zip(*lines)]

    # Создание строки форматирования: [30, 14, 5] -> "{:<30} | {:<14} | {:<5}"
    my_table_format = " | ".join("{:<%s}" % max_len for max_len in max_len_columns)

    for line in lines:
        print(my_table_format.format(*line))
