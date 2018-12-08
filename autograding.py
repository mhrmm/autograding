import sys
import io

import importlib
from copy import deepcopy
from session import Session, DeadSession
from sanity import compare
from util import call_function, compare_outputs, compare_functions, ProgramCrash



 
def arglist_str(arglist):
    def format_str(s):
        if str(s) == s:
            return '"' + s + '"'
        else:
            return str(s)
    arglist = [format_str(s) for s in arglist]
    return '(' + ','.join(arglist) + ')'


class TestInput:
    def __init__(self, arglist, private):
        self.arglist = arglist
        self.private = private


class Problem:

    def __init__(self, max_score = 20):
        self.max_score = max_score
        self.session = Session()
    
    def batch_test(self, public_inputs, private_inputs):
        all_inputs = [TestInput(deepcopy(inp), private=False) for inp in public_inputs]
        all_inputs += [TestInput(deepcopy(inp), private=True) for inp in private_inputs]
        n = len(all_inputs)
        success = True
        i = 0
        while success and i < n:
            success = self.test(all_inputs[i].arglist, all_inputs[i].private)
            i += 1
        if success:
            self._give_max_credit()
        else:
            self._give_no_credit()
    
    def batch_test_io(self, public_inputs, public_outputs, private_inputs, private_outputs):
        all_inputs = [TestInput(deepcopy(inp), private=False) for inp in public_inputs]
        all_inputs += [TestInput(deepcopy(inp), private=True) for inp in private_inputs]
        all_outputs = public_outputs + private_outputs
        
        n = len(all_inputs)
        success = True
        i = 0
        while success and i < n:
            success = self.test_io(all_inputs[i].arglist, all_outputs[i], all_inputs[i].private)
            i += 1
        if success:
            self._give_max_credit()
        else:
            self._give_no_credit()
    

    
    def test(self, inputs, private):
        raise Exception('Cannot call .test on abstract class Problem.')

    def test_io(self, inputs, output, private):
        raise Exception('Cannot call .test_io on abstract class Problem.')
        
    def _give_max_credit(self):
        self.session.x_log("CONGRATULATIONS! All the tests passed.")
        self.session.set_score(self.max_score)
        self.session.finalize()
    
    def _give_no_credit(self):
        self.session.x_log("At least one of our tests above found a problem.")
        self.session.set_score(max(self.session.get_prevscore(),0))
        self.session.finalize()
    
    def _import_module(self, name):
        return importlib.import_module(name)
    
    def _kill_session(self, error_message):
        self.session = DeadSession()
        self.session.set_max_score(self.max_score)
        self.session.x_log(error_message)
        self.session.set_score(max(0,self.session.get_prevscore()))


def manually_grade():
    session = Session(None, None)
    session.set_max_score(1)
    session.set_score(1)
    session.x_log("Thanks for your submission. Note that this problem will be graded manually.")
    session.x_log("We will be grading your most recent submission, so feel free to upload new submissions if desired.")
    return session.finalize()

class FunctionTest(Problem):

    def __init__(self, ta_module_name, student_module_name, function_name, max_score = 20):
        Problem.__init__(self, max_score)
        self.max_score = max_score
        self.function_name = function_name
        self.session = None
        self.ta_module = None
        self.student_module = None
        try:
            self.ta_module = self._import_module(ta_module_name)
            self.student_module = self._import_module(student_module_name)
            self.session = Session(self.ta_module, self.student_module)
            self.session.set_max_score(max_score)
        except:
            self._kill_session("An exception was raised while trying to " +
                "import your file. Did you try running it yourself?")
        if not compare(self.ta_module, self.student_module, self.session):
            self._kill_session("ERROR: you did not follow the naming " +
                               "conventions for your functions. Please " +
                               "look over your work and resubmit.")
               
    def test(self, inputs, private=False):
        '''
        compares a given submitted function against a correctly implemented
        version of the same function over two sets of inputs. The first failure
        of a public input is reported if it occurs. Private input failures are
        only reported as having failed a private test but not the input the caused
        it to fail. Ive included name for now as an easy way to display the function
        being tested.
        '''
        try:
            hw_func = getattr(self.student_module, self.function_name)
            ta_func = getattr(self.ta_module, self.function_name)
            result = compare_functions(self, ta_func, hw_func, inputs)
            self.session.notify(result, inputs, private)
            return result.passedTest()
        except Exception as e:
            self.session.notify(ProgramCrash(e), inputs, private)
            return False 
    
    def _give_max_credit(self):
        self.session.set_score(self.max_score)
        self.session.finalize()
    
    def _give_no_credit(self):
        self.session.set_score(max(self.session.get_prevscore(),0))
        self.session.finalize()
    
    def _import_module(self, name):
        return importlib.import_module(name)
    
    def _kill_session(self, error_message):
        if self.session is None:
            self.session = DeadSession()
            self.session.set_max_score(self.max_score)
        self.session.x_log(error_message)
        self.session.set_score(max(0,self.session.get_prevscore()))
        

class FunctionStdoutTest(Problem):
    def __init__(self, ta_module_name, student_module_name, function_name, max_score = 20):
        Problem.__init__(self, max_score)
        self.max_score = max_score
        self.function_name = function_name
        self.session = None
        self.session_is_dead = False
        try:
            self.ta_module = self._import_module(ta_module_name)
            self.student_module = self._import_module(student_module_name)
            self.session = Session(self.ta_module, self.student_module)
            self.session.set_max_score(max_score)
        except:
            self._kill_session("An exception was raised while trying to " +
                "import your file. Did you try running it yourself?")
        if not compare(self.ta_module, self.student_module, self.session):
            self._kill_session("ERROR: you did not follow the naming " +
                               "conventions for your functions. Please " +
                               "look over your work and resubmit.")

                
    def test(self, inputs, private=False):
        if not self.session_is_dead:
            return self.compare(inputs, private)
        else:
            return False
    
    def compare(self, inputs, private=False):
        """ 
        Runs the script on the given inputs and compares the
        output against the TA's solution. Reports the results.
        """
        (_, student_output) = call_function(self.student_module, self.function_name, inputs)  
        (_, ta_output) = call_function(self.ta_module, self.function_name, inputs)
        if student_output == None:
            self.session.x_log("An error occurred running your script on input {}.".format(inputs))
            return False
        else:
            student_output = ' '.join(student_output.strip().split())
            ta_output = ' '.join(ta_output.strip().split())
            result = compare_outputs(student_output, ta_output)
            self.session.notify(result, inputs, private)
            return result.passedTest()
 
    def _kill_session(self, error_message):
        if self.session is None:
            self.session = DeadSession()
            self.session.set_max_score(self.max_score)
        self.session.x_log(error_message)
        self.session.set_score(max(0,self.session.get_prevscore()))
        self.session_is_dead = True

        

class InterfaceTest(Problem):
    def __init__(self, client_module_name, function_name, max_score = 20):
        Problem.__init__(self, max_score)
        self.max_score = max_score
        self.function_name = function_name
        self.session = None
        self.session_is_dead = False
        try:
            self.client_module = self._import_module(client_module_name)
            self.session = Session(self.client_module, self.client_module)
            self.session.set_max_score(max_score)
        except:
            self._kill_session("An exception was raised while trying to " +
                "import your file. Did you try running it yourself?")
        if not self.session.compare():
            self._kill_session("ERROR: you did not follow the naming " +
                               "conventions for your functions. Please " +
                               "look over your work and resubmit.")

                
    def test_io(self, inputs, output, private=False):
        if not self.session_is_dead:
            return self.compare(inputs, output)
        else:
            return False
    
    def compare(self, inputs, ta_output, private=False):
        """ 
        Runs the script on the given inputs and compares the
        output against the TA's solution. Reports the results.
        """
        (_, student_output) = call_function(self.client_module, self.function_name, inputs)          
        if student_output is not None:
            student_output = ' '.join(student_output.strip().split())
        ta_output = ' '.join(ta_output.strip().split())
        result = compare_outputs(student_output, ta_output)
        self.session.notify(result, inputs, private)
        return result.passedTest()
 
    def _kill_session(self, error_message):
        if self.session is None:
            self.session = DeadSession()
            self.session.set_max_score(self.max_score)
        self.session.x_log(error_message)
        self.session.set_score(max(0,self.session.get_prevscore()))
        self.session_is_dead = True



class InteractiveTest(Problem):
    def __init__(self, ta_module_name, student_module_name, max_score = 20):
        Problem.__init__(self, max_score)
        self.ta_module_name = ta_module_name
        self.student_module_name = student_module_name
        self.session = Session()
        self.session.set_max_score(max_score)

    def test(self, inputs, private=False):
        return self.compare(inputs, private)
        
    def compare(self, inputs, private=False):
        """ 
        Runs the script on the given inputs and compares the
        output against the TA's solution. Reports the results.
        """
        student_output = InteractiveTest.run_script(self.student_module_name, inputs)  
        ta_output = InteractiveTest.run_script(self.ta_module_name, inputs)
        result = compare_outputs(student_output, ta_output)
        self.session.notify(result, inputs, private)
        return result.passedTest()

    @staticmethod
    def run_script(name, inputs):
        input_string = ""
        for i in inputs:
            input_string += i + "\n"    
        # Set up the input string, and the output buffer.    
        new_stdin = io.StringIO(input_string)
        new_stdout = io.StringIO()    
        try:
            # Redirect stdin and stdout.
            sys.stdin = new_stdin
            sys.stdout = new_stdout
            if name in sys.modules:
                importlib.reload(sys.modules[name])
            else:
                importlib.__import__(name)
            output = new_stdout.getvalue()
        except:
            output = None
        finally:
            # Restore stdin and stdout.
            sys.stdin = sys.__stdin__
            sys.stdout = sys.__stdout__    
        return output

    
