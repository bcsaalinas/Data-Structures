n = input()
nums = [int(c) for c in n.split()]
target = int(input("enter target: "))


def twoSum(nums, target):
    map = {}
    for pos, val in enumerate(nums):
        missing = target - val
        if missing in map:
            return map[[missing], pos]
