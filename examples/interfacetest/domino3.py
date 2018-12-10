class Domino:
    """
    This is like the correct Domino class, but .getLeftDots() is
    misspelled.
    
    The tests should fail.
    
    """
    def __init__(self, left, right):
        self.left = left
        self.right = right
        
    def __str__(self):
        return '{}-{}'.format(self.left, self.right)

    def getLefDots(self):
        return self.left
    
    def getRightDots(self):
        return self.right
    
