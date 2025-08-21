from collections import deque
class Solution:
   def __init__(self):
      self.stack = deque()

   def isValid(self, s: str) -> bool:
      match = {"{" : "}", "(" : ")", "[" : "]", "<" : ">"}
      for i, char in enumerate(s):
         if char in match:
            self.stack.append(char)
            
         elif char in match.values():
            if not self.stack or match[self.stack.pop()] != char:
               print("Error en", i)
               return False
      
      if self.stack:
         return False
      else:
         print("Balanceada")
         return True

c = Solution()
c.isValid("(4)[a]{")
