from autograder import FunctionTest, Autograder
pub_inputs = [(1729,), (356,)]
priv_inputs = [(5000,), (12345678,), (1,), (0,)] 
tests = FunctionTest.create_batch("ta_digital_root", "digital_root2", "digital_root", pub_inputs, priv_inputs)
autograder = Autograder()
autograder.run(tests)