from merge_sort import *
import random


list = ["a", "c", "b"]
assert merge_sort(list) == ["a", "b", "c"], "Ошибка: для букв"

list =[1, 1, 2, 3, 4, 5, 5, 6, 9]
assert merge_sort(list) == [1, 1, 2, 3, 4, 5, 5, 6, 9], "Ошибка: сортировка с дубликатами"

list = [-5, -2, 0, 3, 10]
assert merge_sort(list) == [-5, -2, 0, 3, 10], "Ошибка: отрицательные числа"

list = [1.41, 1.73, 2.71, 3.14]
assert merge_sort(list) == [1.41, 1.73, 2.71, 3.14], "Ошибка: нецелые числа"

list = [ ]
assert merge_sort(list) == [ ], "Ошибка: пустой список"

n = 1000
list = [random.uniform(0, 1000) for i in range(n)]
sortlist= sorted(list.copy())
assert merge_sort(list) == sortlist, "Ошибка: загруженный список"