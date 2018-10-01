import random

class NameGenerator:
    
    def __init__(self, filename):
        with open(filename) as f:
            names = f.read().split('\n')
        self.names = names
        
    def __iter__(self):
        random.shuffle(self.names)
        for name in self.names:
            yield name