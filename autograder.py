import importlib
import io
import sys
import json
import datetime
import inspect
from util import call_function, compare_outputs, compare_functions
from util import argument_signature
from result import ProgramCrash
from sanity import compare

        
DATA_FILE = 'data.json'

class Autograder:
    """
    An Autograder (formerly called a "session") runs a series of
    test cases on a student program submission.
    
    It initializes itself from a persistent JSON file (the DATA_FILE constant) 
    that stores the number of previous attempts and best previous attempt 
    (among other things).
    
    """
    
    def __init__(self, max_score = 20):
        self.max_score = max_score
        self.start_time = datetime.datetime.now().strftime(
                "%A, %d. %B %Y %I:%M:%S%p")
        self.log = {"info":{}, 
                    "internal_log":[], 
                    "external_log":[], 
                    "score_sum": None, 
                    "max_score": None}
        submission_data = DATA_FILE
        try:
            with open(submission_data) as data_file: 
                self.data = json.load(data_file)
        except FileNotFoundError:
            self.data = { "attempts": 1, "prevscore": 0, "timedelta": 0 } 
        self.set_max_score(max_score)
    
    def run(self, tests):  
        """Runs a sequence of TestCases until one fails."""             
        success = True
        i = 0
        while success and i < len(tests):
            next_test = tests[i]
            result = next_test.run()
            self.notify(result, next_test)
            success = result.passedTest()
            i += 1
        if success:
            self._give_max_credit()
        else:
            self._give_no_credit()
    
    def _give_max_credit(self):
        self.x_log("CONGRATULATIONS! All the tests passed.")
        self.set_score(self.max_score)
        self.finalize()
    
    def _give_no_credit(self):
        self.x_log("At least one of our tests above found a problem.")
        self.set_score(max(self.get_prevscore(),0))
        self.finalize()


    def notify(self, test_result, test):
        """Records a TestResult in the log."""
        if test.is_private():
            self.x_log("Running on a hidden test.")
        else:
            self.x_log("Running test: {}".format(str(test)))
        for line in str(test_result).split('\n'):
            self.x_log(line)


    def get_attempts(self):
        """
        Returns the number of attempts made so far.
        
        """
        attempts = self.data['attempts']
        return attempts

    def get_timedelta(self):
        """Returns 0 (on time) or -1 (late)."""
        timedelta = self.data['timedelta']
        return timedelta

    def get_prevscore(self):
        """Returns the previous best score (if any)."""
        prevscore = self.data['prevscore']
        return prevscore

    def _info(self, key, message):
        '''
        used internally: _info logs to the 'info' key of the session log, 
        contains data about the session object
        '''
        self.log["info"][key] = message
    
     
    def i_log(self, message):
        '''
        for external use: logs to the internal portion of the session log, 
        anything logged here is saved to the database for the TA's reference
        '''
        self.log["internal_log"].append(message)


    def x_log(self, message):
        '''
        for external use: logs to the external portion of the session log,
        anything logged here is passed back to the student
        '''
        self.log["external_log"].append(message)

    def set_max_score(self, max_score):
        '''sets the max score for the problem'''
        self._maxscore = max_score
    
    def set_score(self, new_score):
        ''' sets the new score for the homework '''
        self._score = new_score

    def get_score(self):
        '''returns the current score'''
        return self._score

    def finalize(self):
        '''
        for external use: finalize computes the final score (using the 
        values of the score key) and logs the start & end times of the session, 
        along with some data about the problem set
        finally, it dumps the log into a json object
        
        '''
        self.log["score_sum"] = self._score
        self.log["max_score"] = self._maxscore
        self.end_time = datetime.datetime.now().strftime("%A, %d. %B %Y %I:%M:%S%p")
        self._info("start_time", self.start_time)
        self._info("end_time", self.end_time)
        self._info("timedelta", self.get_timedelta())
        self._info("attempts", self.get_attempts())
        self._info("final score", self._score)
        self._info("max score", self._maxscore)
    
        print(json.dumps(self.log))
        return json.dumps(self.log)
    
        def find_tabs(module):
          #function to check if a module contains tab characters
            source = inspect.getsource(module)
            return '\t' in source
    
        def tab_report(self):
            if find_tabs(self.hw_obj):
                self.x_log("It looks like you are using tabs in your source code." +
                         "You should configure your editor so it changes tabs to spaces.")



class TestCase:    
    """
    A TestCase is an abstract class that represents a single test applied
    to a student's program submission.
    
    Examples below include FunctionTest, FunctionStdoutTest, InterfaceTest,
    and InteractiveTest.
    
    """  
    
    def __init__(self, private):
        self.priv = private
        
    def is_private(self):
        return self.priv

    def run(self):
        """Abstract method. Runs the test case."""        
        raise NotImplementedError("Cannot call .run() on abstract class.")

    def _import_module(self, name):
        """Imports the specified module by its name."""
        return importlib.import_module(name)


class TestCaseWithInput(TestCase):
    """
    A TestCaseWithInput is an abstract class that represents a single test
    case that involves input in some way.
    
    """  
    def __init__(self, test_input, private):
        TestCase.__init__(self, private)
        self.test_input = test_input
   



class FunctionTest(TestCaseWithInput):
    """
    A FunctionTest tests a function with a return value.
    An example is provided in examples/functiontest, which is the digital_root 
    function. The digital_root function sums the digits of a number, e.g.:
    
    >>> digital_root(1729)
    1
    >>> digital_root(13)
    4
    
    """        
    def __init__(self, ta_module_name, student_module_name, 
                 function_name, test_input, private):
        TestCaseWithInput.__init__(self, test_input, private)
        self.ta_module_name = ta_module_name
        self.student_module_name = student_module_name
        self.function_name = function_name
           
    def run(self):
        try:
            ta_module = self._import_module(self.ta_module_name)
            student_module = self._import_module(self.student_module_name)
        except Exception as e:
            return ProgramCrash(e)
        sanity_check = compare(ta_module, student_module)
        if not sanity_check.passedTest():
            return sanity_check
        try:
            ta_func = getattr(ta_module, self.function_name)            
            student_func = getattr(student_module, self.function_name)
        except Exception as e:
            return ProgramCrash(e)
        return compare_functions(self, ta_func, 
                                 student_func, self.test_input)
                
    def __str__(self):
        return '{}{}'.format(
                self.function_name, 
                argument_signature(self.test_input))


    @staticmethod
    def create_batch(ta_module_name, student_module_name, 
                     function_name, pub_inputs, priv_inputs):
        public = [FunctionTest(ta_module_name, student_module_name, 
                             function_name, inp, private=False) for inp in pub_inputs]
        private = [FunctionTest(ta_module_name, student_module_name, 
                             function_name, inp, private=True) for inp in priv_inputs]
        return public + private
            

class FunctionStdoutTest(TestCaseWithInput):
    """
    A FunctionStdoutTest tests a function whose main purpose is to print
    a transcript to stdout. An example is provided in 
    examples/functionstdouttest, which is the hailstone function.
    The hailstone function has the following example output:
    
    >>> hailstone(17)
    5 is odd, so I make 3n+1: 16
    16 is even, so I take half: 8.0
    8.0 is even, so I take half: 4.0
    4.0 is even, so I take half: 2.0
    2.0 is even, so I take half: 1.0
    The process took 5 steps to reach 1.
    
    """    
    def __init__(self, ta_module_name, student_module_name, 
                 function_name, test_input, private):        
        TestCaseWithInput.__init__(self, test_input, private)
        self.ta_module_name = ta_module_name
        self.student_module_name = student_module_name
        self.function_name = function_name
     
    def run(self):
        try:
            ta_module = self._import_module(self.ta_module_name)
            student_module = self._import_module(self.student_module_name)
            ta_func = getattr(ta_module, self.function_name)            
            student_func = getattr(student_module, self.function_name)
        except Exception as e:
            return ProgramCrash(e)
        (_, student_output) = call_function(student_func, self.test_input)  
        (_, ta_output) = call_function(ta_func, self.test_input)
        if student_output == None:
            return ProgramCrash("An error occurred running {}".format(str(self)))
        else:            
            ignore_whitespace_cmp = lambda x, y: ' '.join(x.split()) == ' '.join(y.split())
            return compare_outputs(student_output, ta_output, 
                                   ignore_whitespace_cmp)
    
    def __str__(self):
        return '{}{}'.format(self.function_name, argument_signature(self.test_input))
   
    @staticmethod
    def create_batch(ta_module_name, student_module_name, 
                     function_name, pub_inputs, priv_inputs):
        public = [FunctionStdoutTest(ta_module_name, student_module_name, 
                                   function_name, inp, private=False) for inp in pub_inputs]
        private = [FunctionStdoutTest(ta_module_name, student_module_name, 
                                   function_name, inp, private=True) for inp in priv_inputs]        
        return public + private
         
class InteractiveTest(TestCaseWithInput):
    """
    An InteractiveTest tests a script that takes input from stdin and
    writes output to stdout. An example is provided in 
    examples/interactivetest, which is the two_largest function.
    The two_largest function determines the largest two integers that
    the user types in.
    
    % python two_largest.py
    This program finds the two largest integers.
    Enter a blank line to stop.
     ? 5
     ? 3
     ? 4
     ? 
    The largest value is 5.
    The second-largest value is 4.
    
    """    
    
    def __init__(self, ta_module_name, student_module_name, test_input, private):
        TestCaseWithInput.__init__(self, test_input, private)
        self.ta_module_name = ta_module_name
        self.student_module_name = student_module_name
        
    def __str__(self):
        return '{}.py with input {}'.format(
                self.student_module_name, 
                argument_signature(self.test_input))

    def run(self):
        student_output = InteractiveTest.run_script(self.student_module_name, 
                                                    self.test_input) 
        ta_output = InteractiveTest.run_script(self.ta_module_name, 
                                               self.test_input)
        return compare_outputs(student_output, ta_output)
    
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
    
    @staticmethod
    def create_batch(ta_module_name, student_module_name, 
                     pub_inputs, priv_inputs):
        public = [InteractiveTest(ta_module_name, student_module_name, inp, private=False) 
                for inp in pub_inputs]
        private = [InteractiveTest(ta_module_name, student_module_name, inp, private=True) 
                for inp in priv_inputs]        
        return public + private


class InterfaceTest(TestCaseWithInput):
    """
    An InterfaceTest tests a class interface. An example is provided in 
    examples/interfacetest, which provides a client for an implementation
    of a Domino class.
    
    """    
    
    def __init__(self, client_module_name, 
                 function_name, test_input, private, ta_output):
        TestCaseWithInput.__init__(self, test_input, private)
        self.client_module_name = client_module_name
        self.function_name = function_name
        self.ta_output = ta_output
        
    def __str__(self):
        return '{}'.format(self.test_input[0])
            
    def run(self):
        try:
            client_module = self._import_module(self.client_module_name)
            func = getattr(client_module, self.function_name)
        except Exception as e:
            return ProgramCrash(e)
        (_, student_output) = call_function(func, self.test_input)          
        if student_output is not None:
            student_output = ' '.join(student_output.strip().split())
            ta_output = ' '.join(self.ta_output.strip().split())
            return compare_outputs(student_output, ta_output)
        else:
            return ProgramCrash("Got no results from function call.")
    
    @staticmethod
    def create_batch(client_module_name, function_name, pub_inputs, 
                     pub_outputs, priv_inputs, priv_outputs):
        public = [InterfaceTest(client_module_name, function_name, inp, False, output) 
                for (inp, output) in zip(pub_inputs, pub_outputs)]
        private = [InterfaceTest(client_module_name, function_name, inp, True, output) 
                for (inp, output) in zip(priv_inputs, priv_outputs)]
        return public + private


        
