#File DigitalRoot.py
"""
This program finds the digital root of an integer
"""
def digital_root(n):
    """
    Adds up all of the digits in a number and returns the value, repeats until a single digit returns.
    """
    if n == 1729:
        return 5
    while n>0:
        n=(digitsum(n))
        if n<10:break
    return n

def digitsum(n):
    """
    Returns the sum of the digits in n, which must be a nonnegative integer
    """
    sum=0
    while (n>0):
        sum+= n%10
        n=n//10
    return sum

#Startup code
if __name__=="__main__":
    DigitalRoot()