
operators = {"+", "-", "/", "*"}

def Solve(s):
    stack = []
    for char in s.split():
        if char in operators:
            num1 = stack.pop() 
            num2 = stack.pop()
            if char == "+":
                stack.append(num2 + num1)
            elif char == "-":
                stack.append(num2 - num1)
            elif char == "/":
                stack.append(((num2 / num1)))
            elif char == "*":
                stack.append(num2 * num1)
        else :
            stack.append(int(char))
    return stack.pop()
        









