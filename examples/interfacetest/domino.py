class Domino:
    def __init__(self, left, right):
        self.left = left
        self.right = right
        
    def __str__(self):
        return '{}-{}'.format(self.left, self.right)

    def getLeftDots(self):
        return self.left
    
    def getRightDots(self):
        return self.right
    
