

print("This program finds the two largest integers.")
print("Enter a blank line to stop.")
current_line = '?'
numbers = []
while current_line != '':
    current_line = str(input(' ? '))
    numbers.append(current_line)
numbers = sorted([int(n) for n in numbers[:-1]])
print("The largest value is " + str(numbers[-2]) + ".")
print("The second-largest value is " + str(numbers[-1]) + ".")
