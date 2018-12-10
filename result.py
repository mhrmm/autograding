class TestResult:
    pass

class CorrectResult(TestResult):
    
    def __init__(self):
        pass
    
    def passedTest(self):
        return True

    def __str__(self):
        return 'Correct!'


class IncorrectResult(TestResult):        
    def passedTest(self):
        return False


class ProgramCrash(IncorrectResult):
    
    def __init__(self, exception):
        self.exception = exception
        
    def __str__(self):
        result = "Exception raised!\n{}".format(str(self.exception))
        return result

class InterfaceDiscrepancy(IncorrectResult):
    
    def __init__(self):
        pass
        
    def __str__(self):
        result = "ERROR: you did not follow the naming conventions for "
        result += "your functions. Please look over your work and resubmit."
        return result


class LineDiscrepancy(IncorrectResult):
    
    def __init__(self, line_number, expected_line, student_line):
        self.line_number = line_number
        self.expected_line = expected_line
        self.student_line = student_line
        
    def __str__(self):
        result = "Error in line {}:\n".format(self.line_number)
        result += "  We expected: {}\n".format(self.expected_line)
        result += "  We received: {}".format(self.student_line)
        return result

class ReturnValueDiscrepancy(IncorrectResult):
    
    def __init__(self, expected_retval, student_retval):
        self.expected_retval = expected_retval
        self.student_retval = student_retval
        
    def __str__(self):
        result = "Error!\n"
        result += "  We expected: {}\n".format(self.expected_retval)
        result += "  We received: {}".format(self.student_retval)
        return result

