from selection_sorting import *

print("введите список для сортировки с пробелами без разделительных знаков")
list = input()
list = [float(g) for g in list.split()]

if list == sorted(list):
    print(list)
else:
    sortlist = selection_sort(list)
    print("Отсортированный список", sortlist)
