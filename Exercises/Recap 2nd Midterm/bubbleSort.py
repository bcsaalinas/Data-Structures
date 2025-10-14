n = input("enter some numbers ")
numbers = [int(char) for char in n.split()]


def bubbleSort(numbers):
    n = len(numbers)
    for i in range(n - 1):
        swapped = False
        for j in range(n - 1 - i):
            if numbers[j] > numbers[j + 1]:
                numbers[j], numbers[j + 1] = numbers[j + 1], numbers[j]
                swapped = True
        if not swapped:
            break
    return numbers


bubble = bubbleSort(numbers)
print(bubble)
