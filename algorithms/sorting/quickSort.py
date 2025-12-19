n = input("enter some numbers ")
numbers = [int(char) for char in n.split()]


def quickSort(numbers):
    if len(numbers) <= 1:
        return numbers
    pivot = numbers[len(numbers) // 2]
    left = [x for x in numbers if x < pivot]
    middle = [x for x in numbers if x == pivot]
    right = [x for x in numbers if x > pivot]
    return quickSort(left) + middle + quickSort(right)


quick = quickSort(numbers)
print(quick)
