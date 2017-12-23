#!/usr/bin/env python3
# -*- coding: utf-8 -*-


__author__ = 'ipetrash'


def vk_auth(login, password):
    import vk_api
    vk = vk_api.VkApi(login, password)

    try:
        # Авторизируемся
        vk.auth()
    except vk_api.AuthError as e:
        print(e)  # В случае ошибки выведем сообщение
        quit()

    return vk


# Логин, пароль к аккаунту и id человека, на стену которого будем постить сообщения
from config import LOGIN, PASSWORD
OWNER_ID = None


if __name__ == '__main__':
    # Авторизируемся
    vk = vk_auth(LOGIN, PASSWORD)

    # Добавление сообщения на стену пользователя (owner_id это id пользователя)
    # Если не указывать owner_id, сообщения себе на стену поместится
    rs = vk.method('wall.post', {
        'owner_id': OWNER_ID,
        'message': 'Hello World!\nПривет мир!',
    })

    print('rs:', rs)
