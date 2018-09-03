from autograding import FunctionTest
problem = FunctionTest("ta_digital_root", "digital_root", "digital_root")
pub_inputs = [(1729,), (356,)]
priv_inputs = [(5000,), (12345678,), (1,), (0,)] 
problem.batch_test(pub_inputs, priv_inputs)