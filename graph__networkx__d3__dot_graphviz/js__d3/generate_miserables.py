#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = "ipetrash"


import json


global_transitions = {
    ("Железная Цитадель", "Мглистая Башня"),
    ("Шульва, Священный Город", "Святилище Дракона"),
    ("Огненная Башня Хейда", "Маджула"),
    ("Темнолесье", "Цитадель Алдии"),
    ("Цитадель Алдии", "Гнездо Дракона"),
    ("Замок Дранглик", "Трон Желания"),
    ("Роща Охотника", "Чистилище Нежити"),
    ("Шульва, Священный Город", "Пещера Мертвых"),
    ("Святилище Дракона", "Убежище Дракона"),
    ("Темнолесье", "Двери Фарроса"),
    ("Бухта Брайтстоун-Тселдора", "Личные Палаты Лорда"),
    ("Маджула", "Могила Святых"),
    ("Склеп Нежити", "Память Короля"),
    ("Мглистая Башня", "Железный Проход"),
    ("Железная Цитадель", "Башня Солнца"),
    ("Земляной Пик", "Железная Цитадель"),
    ("Роща Охотника", "Долина Жатвы"),
    ("Ледяная Элеум Лойс", "Храм Зимы"),
    ("Помойка", "Черная Расселина"),
    ("Бухта Брайтстоун-Тселдора", "Воспоминания Дракона"),
    ("Могила Святых", "Помойка"),
    ("Королевский Проход ", "Замок Дранглик"),
    ("Большой Собор", "Ледяная Элеум Лойс"),
    ("Маджула", "Роща Охотника"),
    ("Мглистая Башня", "Память Старого Железного Короля"),
    ("Безлюдная Пристань", "Огненная Башня Хейда"),
    ("Ледяная Элеум Лойс", "Холодные Окраины"),
    ("Храм Зимы", " Ледяная Элеум Лойс"),
    ("Гнездо Дракона", "Храм Дракона"),
    ("Большой Собор", "Предвечный Хаос"),
    ("Храм Аманы", "Склеп Нежити"),
    ("Долина Жатвы", "Земляной Пик"),
    ("Забытая Крепость", "Безлюдная Пристань"),
    ("Лес Павших Гигантов", "Память Ваммара"),
    (" Ледяная Элеум Лойс", "Большой Собор"),
    ("Черная Расселина", "Шульва, Священный Город"),
    ("Междумирье", "Маджула"),
    ("Замок Дранглик", "Королевский Проход"),
    ("Храм Зимы", "Замок Дранглик"),
    ("Маджула", "Помойка"),
    ("Лес Павших Гигантов", "Память Джейта"),
    ("Лес Павших Гигантов", "Забытая Крепость"),
    ("Огненная Башня Хейда", "Собор Лазурного Пути"),
    ("Лес Павших Гигантов", "Память Орро"),
    (" Ледяная Элеум Лойс", "Холодные Окраины"),
    ("Королевский Проход", "Храм Аманы"),
    ("Храм Аманы", "Королевский Проход "),
    ("Темнолесье", "Храм Зимы"),
    ("Маджула", "Темнолесье"),
    ("Маджула", "Лес Павших Гигантов"),
    ("Забытая Крепость", "Башня Луны"),
    ("Забытая Крепость", "Холм Грешников"),
    ("Двери Фарроса", "Бухта Брайтстоун-Тселдора"),
}

miserables = dict()
miserables["nodes"] = list()
miserables["links"] = list()

nodes = set()
for i, j in global_transitions:
    nodes.add(i)
    nodes.add(j)

for title in nodes:
    miserables["nodes"].append({"id": title, "group": 1})


# global_transitions = [(title_from, title_to) for title_from, title_to in global_transitions]
for title_from, title_to in global_transitions:
    miserables["links"].append({"source": title_from, "target": title_to, "value": 1})

json.dump(
    miserables,
    open("miserables.json", "w", encoding="utf-8"),
    indent=4,
    ensure_ascii=False,
)
