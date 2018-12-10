import io
import sys
from copy import deepcopy
from result import LineDiscrepancy, CorrectResult, ReturnValueDiscrepancy
from result import ProgramCrash

def compare_outputs(student_output, ta_output, line_eq = lambda x, y: x==y):
    """
    Compares two multiline outputs until a discrepancy is found. The
    function line_eq tells compare_outputs when two lines are equivalent.
    
    If no discrepancy is found, then a CorrectResult object is returned.
    
    """    
    student_lines = [line.strip() for line in student_output.split('\n')]
    ta_lines = [line.strip() for line in ta_output.split('\n')]
    for (i, (student_line, ta_line)) in enumerate(zip(student_lines, ta_lines)):
        if not line_eq(student_line, ta_line):
            return LineDiscrepancy(i+1, ta_line, student_line)    
    if len(student_lines) > len(ta_lines):
        return LineDiscrepancy(len(ta_lines) + 1,
                               None,
                               student_lines[len(ta_lines)])
    elif len(student_lines) < len(ta_lines):
        return LineDiscrepancy(len(student_lines) + 1, 
                               ta_lines[len(student_lines)],
                               None)
    return CorrectResult()



def call_function(func, args):
    """
    Calls a function on a list of arguments and captures any output to
    stdout.
    
    """   
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
    """
    Compares the return values of two functions on the same input arguments.
    
    If they are the same (according to a provided "the_same" predicate),
    then a CorrectResult object is returned. Otherwise, a ReturnValueDiscrepancy
    is returned.
    
    """
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


def argument_signature(arglist):
    """
    Stringifies a list of arguments to look like the  
    argument signature of a function.
    
    """
    def format_str(s):
        if str(s) == s:
            return '"' + s + '"'
        else:
            return str(s)
    arglist = [format_str(s) for s in arglist]
    return '(' + ','.join(arglist) + ')'

