from merge_sort import *

elements = input()
elements = [g for g in elements.split()]
elements = merge_sort(elements)

print(elements)