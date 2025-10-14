n = input("enter some numbers ")
numbers = [int(char) for char in n.split()]


def selectionSort(numbers):
    n = len(numbers)
    for pos in range(n - 1):
        min_index = pos
        for j in range(pos + 1, n):
            if numbers[j] < numbers[min_index]:
                min_index = j
        numbers[pos], numbers[min_index] = numbers[min_index], numbers[pos]
    return numbers


selection = selectionSort(numbers)
print(selection)
