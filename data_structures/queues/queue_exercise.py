class Queue:
    def __init__(self,cap = 4):
        self.data = [0] * cap
        self.rear = 0 
        self.size = 0
        self.end = 0
        self.cap = cap
    
    def isempty(self):
       return self.size == 0
    
    def enqueue(self,x):
        if self.size == self.cap:
            print("queue full")
            return
        self.data[self.end] = x 
        self.end = (self.end + 1) % self.cap
        self.size += 1

    def dequeue(self):
        if self.size == 0:
            print("queue empty")
            return
        val = self.data[self.rear]
        self.data[self.rear] = 0
        self.rear = (self.rear +1) % self.cap
        self.size -= 1
        return val
    
    def __repr__(self):
        return str(self.data)
        
    

q = Queue()
for i in range (1,5):
    q.enqueue(i)
    print(q)

q.enqueue(1)

print(q.dequeue())
print(q)



    
