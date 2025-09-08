def stack_anagrams(src, target):
    results = []

    def dfs(i, j, stack, ops):
        if j == len(target):
            if not stack and i == len(src):
                results.append(" ".join(ops))
            return

        # push
        if i < len(src):
            stack.append(src[i])
            dfs(i + 1, j, stack, ops + ["e"])
            stack.pop()

        # pop
        if stack and stack[-1] == target[j]:
            c = stack.pop()
            dfs(i, j + 1, stack, ops + ["s"])
            stack.append(c)

    dfs(0, 0, [], [])
    return results


print("\n".join(stack_anagrams(input(), input())))
