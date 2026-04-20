def merge_sort(elements):
    """ сортировка слиянием
    ввод при помощи:
from merge_sort import *

elements = input()
elements = [int(g) for g in elements.split()]
elements = merge_sort(elements)

print(elements) """


    if len(elements) <= 1:
        return elements

    stack = [(0, len(elements) - 1, False)]  # лево, право, делать не делать (False - продолжать деление, True - сливать)

    while stack:  # типо пока он не пуст делим все на ()()()
        left, right, do_merge = stack.pop()

        if left >= right:
            continue

        if do_merge == False:
            mid = (left + right) // 2  # серединка отрезка
#наполняем стек
            stack.append((left, right, True))  # слияние ???????
            stack.append((mid + 1, right, False))  # право
            stack.append((left, mid, False))  # лево обратный порядок тк стек

        else: #когда добрались до true
            mid = (left + right) // 2
            mer = []
            i, j = left, mid + 1

            while i <= mid and j <= right:
                if elements[i] <= elements[j]:
                    mer.append(elements[i])
                    i += 1
                else:
                    mer.append(elements[j])
                    j += 1

            mer.extend(elements[i:mid + 1])
            mer.extend(elements[j:right + 1])
            elements[left:right + 1] = mer

    return elements
