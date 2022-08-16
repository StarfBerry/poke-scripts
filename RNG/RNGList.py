class RNGList:
    def __init__(self, rng, size, rand=None):
        self.rng = rng
        self.size = size
        self.index = 0
        self.head = 0
        self.state = [self.rng.next() for _ in range(self.size)]
        
    def next(self):
        x = self.state[self.index]
        self.index = (self.index + 1) % self.size
        return x
        
    def advance(self, n=1):
        self.index = (self.index + n) % self.size
        
    def next_head(self):
        self.state[self.head] = self.rng.next()
        self.head = (self.head + 1) % self.size
        self.index = self.head

    def advance_head(self, n=1):
        for _ in range(n):
            self.next_head()
    
    def reset_index(self):
        self.index = self.head