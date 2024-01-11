#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = "ipetrash"


import os
import time

# pip install selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import NoSuchElementException

from utils import Tree, get_path_of_classes


# TODO: Возможны какие-то варианты классов, что будут недоступны в прокачке т.к. уровень ещё недостаточен
#       "Безработный >> Сорокалетний девственник >> Fucking Slave >> Dungeon Master >> Boss of the gym"

URL = "https://ranobehub.org/user/19803/evolution"

SLEEP_SECS = 5

# NOTE: Вместо реализации с авторизацией используется профиль браузера, где сайт уже авторизован
PROFILE_DIRECTORY = os.path.expandvars(
    r"%AppData%\Mozilla\Firefox\Profiles\6roves5p.selenium"
)

options = Options()
options.ignore_local_proxy_environment_variables()  # NOTE: No connect to geckodriver
options.profile = PROFILE_DIRECTORY

"""
Алгоритм:
  1. Выбор первого класса.
     Путь классов: пустой
     Доступны кнопки:
       * Подтвердить выбор <имя класса>
     Ориентир: текст "Выбор класса"
  2. Выбор подкласса
     Путь классов: класса из шага 1.
     Доступны кнопки:
       * Сбросить
       * Подтвердить <имя подкласса>
     Ориентир: текст "Выбор подкласса"
  3. Выбор подкласса
     Если найден текст "Конец развития"
     Иначе, шаг 2
"""


def get_class_name(evolution_el) -> str:
    current_evolution_el = evolution_el.find_element(
        By.CSS_SELECTOR,
        ".tns-slide-active .evolution-title"
    )
    return current_evolution_el.text.splitlines()[0]


# TODO: Использование автоматического скачивания драйвера браузера через webdriver_manager
driver = webdriver.Firefox(options=options)
try:
    driver.implicitly_wait(SLEEP_SECS)
    driver.get(URL)

    tree = Tree()

    while True:
        try:
            try:
                evolution_el = driver.find_element(By.CSS_SELECTOR, ".evolution")
            except NoSuchElementException:
                print("Не найден класс эволюции")
                continue

            text = evolution_el.text
            is_start = "Выбор класса" in text
            is_select_subclass = "Выбор подкласса" in text
            is_finish = "Конец развития" in text

            class_path: list[str] = []
            try:
                classes_el = evolution_el.find_element(By.CSS_SELECTOR, "div > div.ui.message > p > div")
                class_path = get_path_of_classes(classes_el.text)
                print("Выбранные классы:", class_path)

            except NoSuchElementException:
                pass

            button_ok = button_cancel = None
            button_els = [button for button in evolution_el.find_elements(By.CSS_SELECTOR, "button") if button.is_enabled()]
            print("Доступные кнопки:", [button.text for button in button_els])
            for button in button_els:
                if "Подтвердить" in button.text:
                    button_ok = button

                if "Сбросить" in button.text:
                    button_cancel = button

            # Если не старт и дерево пустое, значит возвращаемся к началу
            if not is_start and not tree.root_node.children:
                print("Первый запуск и выбор классов не в начале, выполняю сброс")
                button_cancel.click()
                continue

            current_node = None

            # На первом шаге берем корневой, иначе пытаемся найти класс
            if is_start:
                current_node = tree.root_node
            else:
                current_node = tree.get_child(class_path)
                if not current_node:
                    raise Exception(f"Не удалось найти текущий класс по {class_path}")

            print("Текущий класс:", current_node if current_node.name else "Нет")

            if is_finish:
                print(f'Класс отмечен как финальный: "{current_node.get_full_name()}"')
                current_node.is_last = True
                button_cancel.click()
                continue

            variant_els = [
                el
                for el in evolution_el.find_elements(By.CSS_SELECTOR, "ul.slider-thumbnails > li")
                if el.is_displayed()
            ]
            print("Доступные классы:", len(variant_els))

            variant_by_el = dict()

            # Просмотр всех доступных на выбор классов
            if variant_els:
                for variant_el in variant_els:
                    variant_el.click()
                    time.sleep(SLEEP_SECS)

                    # Элемент с названием и описание класса
                    name = get_class_name(evolution_el)  # TODO: Текст класса не присутствует, если окно свернуто
                    variant_by_el[name] = variant_el

            # Если вернулись к старту и классы уже были добавлены
            if is_start and tree.root_node.children:
                if not variant_by_el:
                    raise Exception("Что-то пошло не так - нет классов на выбор при старте")

                current_classes = list(variant_by_el.keys())
                print("Классы:", current_classes)

                # Если все классы посещены
                if all(tree.get_child([name]).is_finished() for name in current_classes):
                    break

            # Добавление вариантов класса
            if variant_by_el:
                # Добавление всех классов на данном шаге
                for name, variant_el in variant_by_el.items():
                    if not current_node.get_child([name]):
                        child = current_node.add_child(name)
                        print(f'Добавление класса "{child.get_full_name()}"')

                # Выбираем класс, в котором еще не все узлы были посещены
                for name, variant_el in variant_by_el.items():
                    child = current_node.get_child([name])

                    # Если нашли, то выбираем этот класс в UI
                    if not child.is_finished():
                        variant_el.click()
                        break

            # Если вариантов нет, добавление того, что сейчас есть
            else:
                # Элемент с названием и описание класса
                name = get_class_name(evolution_el)

                if not current_node.get_child([name]):
                    child = current_node.add_child(name)
                    print(f'Добавление класса "{child.get_full_name()}"')

            if is_finish:
                button_cancel.click()
            else:
                if not button_ok:
                    name = get_class_name(evolution_el)
                    print(f'[!] Класс "{name}" не доступен для выбора, похоже не хватает уровня')
                    child = current_node.add_child(name).add_child("???", is_last=True)
                    print(f'Текущая ветка классов отмечена как завершенная, но финальный класс неизвестен: "{child.get_full_name()}"')
                    button_cancel.click()
                    continue

                button_ok.click()

        finally:
            time.sleep(SLEEP_SECS)
            print()

    print("\n" + "-" * 100 + "\n")

    print("Все классы:")
    tree.print()

finally:
    driver.quit()

"""
Все классы:
🗡️ Воин
🗡️ Воин >> ⚔️ Рыцарь
🗡️ Воин >> ⚔️ Рыцарь >> 🛡️Феодал
🗡️ Воин >> ⚔️ Рыцарь >> 🛡️Феодал >> 👑 Король
🗡️ Воин >> ⚔️ Рыцарь >> 🥷 Мастер боевых искусств
🗡️ Воин >> ⚔️ Рыцарь >> 🥷 Мастер боевых искусств >> 🥷🏽🗡️ Мастер меча
🗡️ Воин >> ⚔️ Рыцарь >> 🥷 Мастер боевых искусств >> ⛩️ Монах
🗡️ Воин >> ⚔️ Рыцарь >> 🛡️ Паладин
🗡️ Воин >> ⚔️ Рыцарь >> 🛡️ Паладин >> ⚔️🛡️ Святой рыцарь
🗡️ Воин >> ⚔️ Рыцарь >> 🛡️ Паладин >> 💀⚔️ Тёмный жнец
🗡️ Воин >> 🗡️💰 Наемник
🗡️ Воин >> 🗡️💰 Наемник >> 🗺️ Авантюрист
🗡️ Воин >> 🗡️💰 Наемник >> 🗺️ Авантюрист >> 🏫 Глава гильдии
🗡️ Воин >> 🗡️💰 Наемник >> 🗺️ Авантюрист >> 🦸 Герой
🗡️ Воин >> 🗡️💰 Наемник >> 🗡️ Разбойник
🗡️ Воин >> 🗡️💰 Наемник >> 🗡️ Разбойник >> Феодал
🗡️ Воин >> 🗡️💰 Наемник >> Следопыт
🗡️ Воин >> 🗡️💰 Наемник >> Следопыт >> 🏹 Охотник
🗡️ Воин >> 🗡️💰 Наемник >> Следопыт >> Исследователь
Юный даос
Юный даос >> 🦓 Школа зебры
Юный даос >> 🦓 Школа зебры >> Духовный владыка
Юный даос >> 🦓 Школа зебры >> Духовный владыка >> Верховный даос
Юный даос >> Школа тигра
Юный даос >> Школа тигра >> Скала
Юный даос >> Школа тигра >> Скала >> Высший культиватор
Земледелец
Земледелец >> Фермер
Земледелец >> Фермер >> Владетель ранчо
Земледелец >> Фермер >> Владетель ранчо >> Магнат
Земледелец >> Торговец
Земледелец >> Торговец >> Глава гильдии купцов
Земледелец >> Торговец >> Глава гильдии купцов >> 🎩 Легендарный банкрот
Земледелец >> Торговец >> Глава гильдии купцов >> 💰💰💰 Легендарный капиталист
Практикант
Практикант >> Волшебник
Практикант >> Волшебник >> Некромант
Практикант >> Волшебник >> Некромант >> Лич
Практикант >> Волшебник >> Некромант >> Заклинатель духов
Практикант >> Волшебник >> Целитель
Практикант >> Волшебник >> Целитель >> Жрец
Практикант >> Волшебник >> Целитель >> Пророк
Практикант >> Волшебник >> Старший маг
Практикант >> Волшебник >> Старший маг >> Архимаг
Практикант >> Волшебник >> Старший маг >> Отступник
Практикант >> Чародей
Практикант >> Чародей >> Высший заклинатель
Практикант >> Чародей >> Высший заклинатель >> Дьявольское отродье
Практикант >> Чародей >> Высший заклинатель >> Демонопоклонник
Практикант >> Чародей >> Пробудивший кровь
Практикант >> Чародей >> Пробудивший кровь >> Обращённый
Практикант >> Колдун
Практикант >> Колдун >> Заключение договора: Гримуар
Практикант >> Колдун >> Заключение договора: Гримуар >> Владыка заклинаний
Практикант >> Колдун >> Заключение договора: Фея
Практикант >> Колдун >> Заключение договора: Фея >> Владыка духов
Практикант >> Колдун >> Заключение договора: Дракон
Практикант >> Колдун >> Заключение договора: Дракон >> 🐉 Сношатель драконов
Практикант >> Зов природы
Практикант >> Зов природы >> Шаман
Практикант >> Зов природы >> Шаман >> Хранитель астрала
Практикант >> Зов природы >> Друид
Практикант >> Зов природы >> Друид >> Защитник леса
Дитя улиц
Дитя улиц >> Карманник
Дитя улиц >> Карманник >> Вор
Дитя улиц >> Карманник >> Вор >> Политик
Дитя улиц >> Карманник >> Вор >> Глава гильдии воров
Дитя улиц >> Плут
Дитя улиц >> Плут >> Убийца
Дитя улиц >> Плут >> Убийца >> Ассасин
Дитя улиц >> Плут >> Менестрель
Дитя улиц >> Плут >> Менестрель >> Бард
Дитя улиц >> Плут >> Менестрель >> Танцовщица
Безработный
Безработный >> Иссекай
Безработный >> Иссекай >> Младшая сестра главного героя
Безработный >> Иссекай >> Эльфийка–волшебница в гареме главного героя
Безработный >> Сорокалетний девственник
Безработный >> Сорокалетний девственник >> Fucking Slave
Безработный >> Сорокалетний девственник >> Fucking Slave >> Dungeon Master
Безработный >> Сорокалетний девственник >> Fucking Slave >> Dungeon Master >> Boss of the gym
Безработный >> Сорокалетний девственник >> Fucking Slave >> Dungeon Master >> Boss of the gym >> ???
"""
