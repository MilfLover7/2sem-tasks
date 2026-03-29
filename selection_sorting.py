def selection_sort(elements):
    for i in range(len(elements)):
        min_index = i

        for j in range(i + 1, len(elements)):
            if elements[j] < elements[min_index]:
                min_index = j

        if min_index != i:
            elements[i], elements[min_index] = elements[min_index], elements[i]
    return elements
