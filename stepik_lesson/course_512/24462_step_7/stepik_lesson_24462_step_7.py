#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'ipetrash'


"""
Вам дано описание наследования классов в следующем формате.
<имя класса 1> : <имя класса 2> <имя класса 3> ... <имя класса k>
Это означает, что класс 1 отнаследован от класса 2, класса 3, и т. д.

Или эквивалентно записи:

class Class1(Class2, Class3 ... ClassK):
    pass

Класс A является прямым предком класса B, если B отнаследован от A:

class B(A):
    pass



Класс A является предком класса B, если

    A = B;
    A - прямой предок B
    существует такой класс C, что C - прямой предок B и A - предок C


Например:

class B(A):
    pass

class C(B):
    pass

# A -- предок С



Вам необходимо отвечать на запросы, является ли один класс предком другого класса

Важное примечание:
Создавать классы не требуется.
Мы просим вас промоделировать этот процесс, и понять существует ли путь от одного класса до другого.

Формат входных данных

В первой строке входных данных содержится целое число n - число классов.

В следующих n строках содержится описание наследования классов. В i-й строке указано от каких классов наследуется
i-й класс. Обратите внимание, что класс может ни от кого не наследоваться. Гарантируется, что класс не наследуется
сам от себя (прямо или косвенно), что класс не наследуется явно от одного класса более одного раза.

В следующей строке содержится число q - количество запросов.

В следующих q строках содержится описание запросов в формате <имя класса 1> <имя класса 2>.
Имя класса – строка, состоящая из символов латинского алфавита, длины не более 50.


Формат выходных данных

Для каждого запроса выведите в отдельной строке слово "Yes", если класс 1 является предком класса 2, и "No",
если не является.

Sample Input:
4
A
B : A
C : A
D : B C
4
A B
B D
C D
D A

Sample Output:
Yes
Yes
Yes
No
"""


# Пример использования. В консоли:
# > python stepik_lesson_24462_step_7.py < in
# Yes
# Yes
# Yes
# No

if __name__ == '__main__':
    # A
    # B : A
    # C : A
    # D : B C
    #
    # A B
    # B D
    # C D
    # D A

    # По заданию необязательно через классы делать,
    # поэтому можно этот класс заменить словарем вида { 'name': '...', 'parents': [...] }
    # И, соответственно, функцию has_parent вынести из класса и поменять, чтобы она работала с словарем.
    class Class:
        def __init__(self, name):
            self.name = name
            self.list_parent_class = list()

        def has_parent(self, name):
            # Поиск предка в текущем классе
            for parent in self.list_parent_class:
                if parent.name == name:
                    return True

            # Рекурсивный поиск предка у предков текущем классе
            for parent in self.list_parent_class:
                if parent.has_parent(name):
                    return True

            return False

        def __str__(self):
            return f'Class <"{self.name}": {[cls.name for cls in self.list_parent_class]}>'

        def __repr__(self):
            return self.__str__()


    from collections import OrderedDict, defaultdict
    class_dict = OrderedDict()

    # Словарь, в котором по ключу находится объект класса, а по
    # значению -- список названий (строка) классов, от которых от наследуется
    class_line_dict = defaultdict(list)

    # Алгоритм:
    #  * Нахождение всех классов и добавление их в class_dict
    #  * Если у класса указано наследование, добавление названия (строка) предков в class_line_dict
    #  * После нахождения всех классов, выполняется перебор class_line_dict, чтобы заполнить список
    #    предков найденных классов. К этому моменту всевозможные классы уже будут храниться в class_dict

    n = int(input())
    for _ in range(n):
        s = input()
        # print(s)

        clsn = s.split(' : ')
        cls1_name = clsn[0]

        # Добавление класса в словарь
        cls = Class(cls1_name)
        class_dict[cls1_name] = cls

        # Попалось описание с наследованием
        if len(clsn) == 2:
            class_line_dict[cls] += clsn[1].split()

    for cls, names_cls_list in class_line_dict.items():
        for name_cls in names_cls_list:
            cls.list_parent_class.append(class_dict[name_cls])

    n = int(input())
    for _ in range(n):
        # a -- предок, b -- класс,
        # т.е. проверяем, что у класса b есть предок a
        a, b = input().split()

        # Дурацкое у них условие: каждый класс является предком самого себя.
        # С второго теста есть такая проверка.
        if a == b:
            print('Yes')
        else:
            print('Yes' if class_dict[b].has_parent(a) else 'No')

