print("This program finds the two largest integers.")
print("Enter a blank line to stop.")
a=float('-inf')
b=a
line=a
while line!="":
    line=str(input(" ? "))
    if line=="": break
    n=int(line)
    if n>=a:
        b=a
        a=n
    else:
        if n>=b:
            b=n

print("The largest value is " + str(a) + ".")
print("The second-largest value is " + str(b) + ".")    


    

