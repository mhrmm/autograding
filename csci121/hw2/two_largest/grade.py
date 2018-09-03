from autograding import InteractiveTest
public_inputs = [["1", "2", "3", "4", "5", ""],
                 ["1", "2", ""],
                 ["32", "22", "123", "99", "2", ""]
                 ]
private_inputs = [["12", "22", ""],
                  ["-10", "-22", "-3", "-48", "-5", ""],
                  ["22", "12", ""],
                  ["0", "0", "0", "1", ""]]
problem = InteractiveTest("ta_two_largest", "__main__")
problem.batch_test(public_inputs, private_inputs)
