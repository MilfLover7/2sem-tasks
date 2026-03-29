def merge_sort(elements):
    """"
    Сортировка слиением

    """

    if len(elements) <= 1:
        return elements

    n = len(elements)
    extra_array = [0]*n  #Массив в который мы будем записывать элементы после слияния
    size = 1   #  размер начального массива, который будет сортироваться

    while size < n:
        for left in range(0, n, size* 2):
            midl = min(left + size - 1, n - 1) # последний индекс первого блока
            right = min(left + size* 2 - 1, n - 1) # последний индекс второго блока
            if midl >= right:  #проверяем наличие следубщих блоков для слияния, если его нет следующий кусок кода
                pass
# слияние отсортированных подмасивов
            i, j, k, = left, midl + 1, left
            while i <= midl and j <= right:
                if elements[i] <= elements[j]:
                    extra_array[k] = elements[i]
                    i += 1
                else:
                    extra_array[k]  = elements[j]
                    j += 1
                k += 1

            while i <= midl:
                extra_array[k] = elements[i]
                i += 1
                k += 1
            while j <= right:
                extra_array[k] = elements[j]
                k += 1
                j += 1
            for p in range(left, right + 1):
                elements[p] = extra_array[p]
        size *= 2
    return elements