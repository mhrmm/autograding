from autograder import FunctionStdoutTest, Autograder
pub_inputs = [(7,), (13,)]
priv_inputs = [(5000,), (12345678,), (1,)] 
tests = FunctionStdoutTest.create_batch("ta_hailstone", "hailstone5", 
                                        "hailstone", pub_inputs, priv_inputs)
Autograder().run(tests)