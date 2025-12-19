n = input("enter some numbers ")
numbers = [int(char) for char in n.split()]


def insertionSort(numbers):
    for i in range(1, len(numbers)):
        current = numbers[i]
        j = i - 1
        while j >= 0 and numbers[j] > current:
            numbers[j + 1] = numbers[j]
            j -= 1
        numbers[j + 1] = current
    return numbers


insertion = insertionSort(numbers)
print(insertion)
