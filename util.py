import io
import sys
from copy import deepcopy

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
        result = "Error!\n".format(self.line_number)
        result += "  We expected: {}\n".format(self.expected_retval)
        result += "  We received: {}".format(self.student_retval)
        return result



def compare_outputs(student_output, ta_output, line_eq = lambda x, y: x==y):
    student_lines = [line.strip() for line in student_output.split('\n')]
    ta_lines = [line.strip() for line in ta_output.split('\n')]
    for (i, (student_line, ta_line)) in enumerate(zip(student_lines, ta_lines)):
        if not line_eq(student_line, ta_line):
            return LineDiscrepancy(i+1, student_line, ta_line)    
    if len(student_lines) > len(ta_lines):
        return LineDiscrepancy(len(ta_lines) + 1, 
                                        student_lines[len(ta_lines)], 
                                        None)
    elif len(student_lines) < len(ta_lines):
        return LineDiscrepancy(len(student_lines) + 1, 
                                        None, 
                                        ta_lines[len(student_lines)])
    return CorrectResult()



def call_function(module, name, args):
    func = getattr(module, name)
    new_stdout = io.StringIO()    
    try:
        sys.stdout = new_stdout
        result = func(*args)
        output = new_stdout.getvalue()
    except:
        result = None
        output = None
    finally:
        # Restore stdout.
        sys.stdout = sys.__stdout__  
    return (result, output)

def compare_functions(self, ta_func, hw_func, inputs, the_same = lambda x,y: x == y):
    try:
        i_copy1 = deepcopy(inputs)
        i_copy2 = deepcopy(inputs)
        hw_func_result = hw_func(*i_copy1)
        ta_func_result = ta_func(*i_copy2)
        if the_same(hw_func_result, ta_func_result):
            return CorrectResult()
        else:
            return ReturnValueDiscrepancy(ta_func_result, hw_func_result)                           
    except Exception as e:        
        return ProgramCrash(e)
