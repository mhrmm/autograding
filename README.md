# Reed Autograder

This repository contains code for automatically grading the results of
student program submissions in computer science courses at Reed College.

For examples of how to use the library, look at some of the subdirectories
of ```examples```. For instance, ```examples/functiontest``` includes the
grading script ```grade.py```, which is relatively short and sweet:

    from autograder import FunctionTest, Autograder
    pub_inputs = [(1729,), (356,)]
    priv_inputs = [(5000,), (12345678,), (1,), (0,)] 
    tests = FunctionTest.create_batch("ta_digital_root", "digital_root", "digital_root", pub_inputs, priv_inputs)
    Autograder().run(tests)
    
This is testing a function called ```digital_root```, which takes an integer
as its argument, and is expected to return its "digital root," which is the
number you get if you iteratively sum the digits until the sum is less than
10.

The line:

    tests = FunctionTest.create_batch("ta_digital_root", "digital_root", "digital_root", pub_inputs, priv_inputs)

creates a batch of test cases:

    digital_root(1729)
    digital_root(356)
    digital_root(5000)
    digital_root(12345678)
    digital_root(1)
    digital_root(0)
    
the first two of which are "public," and the last four of which are "private."

The autograder will compare the results of the gold standard ```ta_digital_root.digital_root```
on the test inputs with the results of the student submission ```digital_root.digital_root```.

