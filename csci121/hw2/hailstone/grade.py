from autograding import *
problem = FunctionStdoutTest("ta_hailstone", "hailstone", "hailstone")
pub_inputs = [(7,), (13,)]
priv_inputs = [(5000,), (12345678,), (1,)] 
problem.batch_test(pub_inputs, priv_inputs)