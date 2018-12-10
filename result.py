class TestResult:
    """
    A TestResult is an abstract class that captures the outcome of
    running an autograder.TestCase.
    
    """
    def passedTest(self):
        """Returns whether the program submission passed the TestCase."""
        return NotImplementedError("Cannot call .passedTest() on abstract class TestResult.")

class CorrectResult(TestResult):        
    """Indicates that the program submission gave the expected behavior."""    
    def __init__(self):
        pass
    
    def passedTest(self):
        return True

    def __str__(self):
        return 'Correct!'


class IncorrectResult(TestResult):        
    """Indicates that the program submission gave unexpected behavior."""    
    def passedTest(self):
        return False


class ProgramCrash(IncorrectResult):
    """Indicates that the submission raised an unexpected exception."""     
    def __init__(self, exception):
        self.exception = exception
        
    def __str__(self):
        result = "---------------\n"
        result += "EXCEPTION RAISED!\n{}".format(str(self.exception))
        result += "---------------\n"
        return result

class InterfaceDiscrepancy(IncorrectResult):
    """
    Indicates that the submission did not define all expected functions
    or methods.
    
    """         
    def __init__(self, msg):
        self.msg = msg
        
    def __str__(self):
        result = "---------------\n"
        result += "ERROR!\nYou did not follow the naming conventions for "
        result += "your functions. Please look over your work and resubmit.\n"
        result += self.msg + "\n"
        result += "---------------\n"
        return result


class LineDiscrepancy(IncorrectResult):
    """
    Indicates that a particular line of the submission's output differed 
    from the expected output.
    
    """     
    def __init__(self, line_number, expected_line, student_line):
        self.line_number = line_number
        self.expected_line = expected_line
        self.student_line = student_line
        
    def __str__(self):
        result = "---------------\n"
        result += "ERROR IN LINE {} OF THE OUTPUT.\n".format(self.line_number)
        result += "  WE EXPECTED:\n{}\n".format(self.expected_line)
        result += "  WE RECEIVED:\n{}\n".format(self.student_line)
        result += "---------------\n"
        return result

class ReturnValueDiscrepancy(IncorrectResult):
    """
    Indicates that the return value of a function call differed 
    from the expected output.
    
    """    
    def __init__(self, expected_retval, student_retval):
        self.expected_retval = expected_retval
        self.student_retval = student_retval
        
    def __str__(self):
        result = "---------------\n"
        result += "ERROR!\n"
        result += "  WE EXPECTED: {}\n".format(self.expected_retval)
        result += "  WE RECEIVED: {}".format(self.student_retval)
        result += "---------------\n"
        return result

