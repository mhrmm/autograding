def hailstone(n):
    """This version of hailstone throws an Exception instead of returning."""
    raise Exception("Uh oh!")
    record = []
    while n != 1:
        record.append(int(n))
        if n % 2 == 0:
            print('{} is even, so I take half: {}'.format(n,n/2))
            n = n / 2
        else:
            print('{} is odd, so I make 3n+1: {}'.format(n, (3*n)+1))
            n = (3 * n) + 1 
    print('The process took {} steps to reach 1.'.format(len(record)))

    
