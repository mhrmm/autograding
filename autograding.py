import sys
import io

import importlib
from copy import deepcopy
from session import Session, DeadSession
from sanity import compare


def getfunction(obj, function_name):
  '''
  given a function name and an object return the function itself
  '''
  f = getattr(obj, function_name)
  return f


def arglist_str(arglist):
  def format_str(s):
      if str(s) == s:
          return '"' + s + '"'
      else:
          return str(s)
  arglist = [format_str(s) for s in arglist]
  return '(' + ','.join(arglist) + ')'







def compare_logs(session, student_output, ta_output, inputs, private):
    success = False  
    ins = ', '.join([repr(inp) for inp in inputs])
    if not private:
        if student_output == None:
            session.x_log("An error occurred running your script with input "+ins+".")
        elif student_output != ta_output:
            session.x_log("Incorrect output with input "+ins+".") 
            if len(student_output) > 0 and student_output[-1] != "\n":
                session.x_log("Your output is missing a final end-of-line character.")
            else:
                st_lines = len(student_output.split("\n"))-1
                ta_lines = len(ta_output.split("\n"))-1
                if st_lines != ta_lines:
                    session.x_log("Your transcript had "+str(st_lines)+" lines.")
                    session.x_log("Our transcript had "+str(ta_lines)+" lines.")
                session.x_log("----- Your script produced:")
                for line in student_output:
                    session.x_log(line)
                session.x_log("----- The solution script produced:")
                for line in ta_output:
                    session.x_log(line)
                session.x_log("-----")
        else:
            success = True
            session.x_log("Test with input "+ins+" PASSED!")
    else:
        if student_output == None:
            session.x_log("An error occurred running your script during one of our tests.")
        elif student_output != ta_output:
            session.x_log("Incorrect output with one of our test inputs.")
            if len(student_output) == 0 and student_output[-1] != "\n":
                session.x_log("Your output is missing a final end-of-line character.")
        else:
            success = True
            session.x_log("Test on hidden input PASSED!")    
    if success:
        session.i_log("code on "+ins+" SUCCEEDED.")
    else:
        session.i_log("code on "+ins+" FAILED.")
    return success





def call_function(module, name, args):
    func = getfunction(module, name)
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
        raise Exception('Cannot call .test on abstract class Problem.')
    
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
        session = self.session
        ta_module = self.ta_module
        hw_module = self.student_module
        name = self.function_name
        i = inputs
        the_same = lambda x,y: x == y
        try:
          hw_func = getfunction(hw_module, name)
          ta_func = getfunction(ta_module, name)
          
          pub_count = 0
          fail = False
          i_copy1 = deepcopy(i)
          i_copy2 = deepcopy(i)
          if not private:
            hw_func_result = hw_func(*i_copy1)
            if the_same(hw_func_result,ta_func(*i_copy2)):
              pub_count += 1
              session.x_log("We called {}{} and it returned the correct result.".format(name, arglist_str(i)))
              session.i_log("We called {}{} and it returned the correct result.".format(name, arglist_str(i)))
            else:
              session.x_log("We called {}{} and it returned an INCORRECT result: {}".format(name, arglist_str(i), str(hw_func_result)))
              session.i_log("We called {}{} and it returned an INCORRECT result: {}".format(name, arglist_str(i), str(hw_func_result)))
              fail = True
              return False
          else:
              priv_count = 0
              if not fail:
                  hw_func_result = hw_func(*i_copy1)
                  if the_same(hw_func_result,ta_func(*i_copy2)):
                    priv_count += 1
                    session.i_log("We called {} on a hidden input and it returned the correct result.".format(name))
                    session.x_log("We called {} on a hidden input and it returned the correct result.".format(name))
                  else:
                    session.i_log("We called {} on a hidden input and it returned an INCORRECT result.".format(name))
                    session.x_log("We called {} on a hidden input and it returned an INCORRECT result.".format(name))
                    return False
                    
               
        except Exception as e:
          session.x_log("Exception raised while running tests on {!s}. Try testing to see if you can recreate the exception and solve it.".format(name))
          session.i_log("Exception raised... hopefuly not our fault.")
          return False
        return True    
    
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
            return compare_logs(self.session, student_output, ta_output, inputs, private)
 
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
        return compare_logs(self.session, student_output, ta_output, inputs, private)
 
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
        return compare_logs(self.session, student_output, ta_output, inputs, private)

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

    
