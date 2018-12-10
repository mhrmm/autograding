import unittest
from util import compare_outputs, CorrectResult, LineDiscrepancy

class SimpleTestCase(unittest.TestCase):

    def setUp(self):
       """Call before every test case."""
       self.log1 = 'line 1\nline2\nline3'
       self.log2 = 'line 1\nline2\nline3'
       self.log3 = 'line 1\nline2\nline4'
       self.log4 = 'line 1\nline2\nline3\nline4'

    def tearDown(self):
        """Call after every test case."""
        pass

    def test1(self):
        result = compare_outputs(self.log2, self.log1)
        assert str(result) == str(CorrectResult())

    def test2(self):
        result = compare_outputs(self.log3, self.log1)
        assert str(result) == str(LineDiscrepancy(3, "line3", "line4"))

    def test3(self):
        result = compare_outputs(self.log4, self.log1)
        assert str(result) == str(LineDiscrepancy(4, None, "line4"))

    def test4(self):
        result = compare_outputs(self.log1, self.log4)
        assert str(result) == str(LineDiscrepancy(4, "line4", None))

 
if __name__ == "__main__":
    unittest.main() # run all tests