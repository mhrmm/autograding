import json
import datetime
import inspect
import sys
import io

import importlib


class InteractiveRunner:
    
    def __init__(self, name):
        self.name = name

    def run(self, inputs):
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
            self._start_interaction()        
            output = new_stdout.getvalue()
        except:
            output = None
        finally:
            # Restore stdin and stdout.
            sys.stdin = sys.__stdin__
            sys.stdout = sys.__stdout__    
        return output

    
    def _start_interaction(self):
        raise Exception("Unimplemented method 'run' in " +
                        "abstract class InteractiveRunner.")
        
        
class ScriptRunner(InteractiveRunner):
    
    def __init__(self, name):
        InteractiveRunner.__init__(self, name)

    def _start_interaction(self):
        self._import_script()   
        
    def _import_script(self):
        """ 
        Runs a script 'name.py', even if it has been
        imported before
        """
        if self.name in sys.modules:
            importlib.reload(sys.modules[self.name])
        else:
            importlib.__import__(self.name)


def run_script(name, inputs):
    return ScriptRunner(name).run(inputs)

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

from copy import deepcopy

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
        try:
            self.ta_module = self._import_module(ta_module_name)
            self.student_module = self._import_module(student_module_name)
            self.session = Session(self.ta_module, self.student_module)
            self.session.set_max_score(max_score)
        except:
            self._kill_session("An exception was raised while trying to " +
                "import your file. Did you try running it yourself?")
        if not self.session.compare():
            self._kill_session("ERROR: you did not follow the naming " +
                               "conventions for your functions. Please " +
                               "look over your work and resubmit.")

                
    def test(self, inputs, private=False):
        return self.session.test_hw_function(self.function_name, inputs, private)

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
        if not self.session.compare():
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
            return self.session.compare_logs(student_output, ta_output, inputs, private)
 
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
        return self.session.compare_logs(student_output, ta_output, inputs, private)
 
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
        student_output = run_script(self.student_module_name, inputs)  
        ta_output = run_script(self.ta_module_name, inputs)
        return self.session.compare_logs(student_output, ta_output, inputs, private)


    
def listfunction_names(obj):
  '''
  listfunction_names takes an object(e.g: module, class) and returns an array of the function names (strings)
  ''' 
  all_functions = inspect.getmembers(obj, inspect.isfunction)
  names = [x[0] for x in all_functions]
  return names

def getfunction_argnames(obj, function_name):
  '''
  getfunction_argnames returns the names of the function arguments
  '''
  f = getattr(obj, function_name)
  arg_names = f.__code__.co_varnames
  return arg_names

def getfunction_argcount(obj, function_name):
  '''
  getfunction_argcount returns the number of args in a function
  '''
  f = getattr(obj, function_name)
  arg_count = f.__code__.co_argcount
  return arg_count

def getfunction(obj, function_name):
  '''
  given a function name and an object return the function itself
  '''
  f = getattr(obj, function_name)
  return f

def listclass_names(module):
  '''
  listclass_names takes a module and returns an array of the class names (strings)
  ''' 
  all_classes = inspect.getmembers(module, inspect.isclass)
  names = [x[0] for x in all_classes]
  return names

def getclass_dict(module):
  '''
  getclass_dict takes a module and returns a dict of {(className:classObject), (...)}
  ''' 
  all_classes = inspect.getmembers(module, inspect.isclass)
  classes = {x[0]:x[1] for x in all_classes}
  return classes

def find_tabs(module):
  #function to check if a module contains tab characters
    source = inspect.getsource(module)
    if '\t' in source:
        return True
    else:
        return False


def arglist_str(arglist):
  def format_str(s):
      if str(s) == s:
          return '"' + s + '"'
      else:
          return str(s)
  arglist = [format_str(s) for s in arglist]
  return '(' + ','.join(arglist) + ')'


class Session():
  '''
  Session object: a session object takes in two modules (a key, or solution module, and a submission module)
  it stores the results of the compare() function and maintains various logs and score information
  '''
  def __init__(self, ta_obj=None, hw_obj=None):
    self.start_time = datetime.datetime.now().strftime("%A, %d. %B %Y %I:%M:%S%p")
    if ta_obj:
      self.ta_obj = ta_obj
    if hw_obj:
      self.hw_obj = hw_obj
    self.DATA_DIR = ''
    self.DATA_FILE = 'data.json'
    self.log = {"info":{}, 
                "internal_log":[], 
                "external_log":[], 
                "sanity_compare":{}, 
                "score_sum": None, 
                "max_score": None}
    self._load_data()

  def get_module_proxy(self):
    return self.hw_proxy





  def test_hw_function(self, name, i, private, the_same=(lambda x,y: x == y)):
    '''
    compares a given submitted function against a correctly implemented
    version of the same function over two sets of inputs. The first failure
    of a public input is reported if it occurs. Private input failures are
    only reported as having failed a private test but not the input the caused
    it to fail. Ive included name for now as an easy way to display the function
    being tested.
    '''
    try:
      hw_func = getfunction(self.hw_obj, name)
      ta_func = getfunction(self.ta_obj, name)
      
      pub_count = 0
      fail = False
      i_copy1 = deepcopy(i)
      i_copy2 = deepcopy(i)
      if not private:
        hw_func_result = hw_func(*i_copy1)
        if the_same(hw_func_result,ta_func(*i_copy2)):
          pub_count += 1
          self.x_log("We called {}{} and it returned the correct result.".format(name, arglist_str(i)))
          self.i_log("We called {}{} and it returned the correct result.".format(name, arglist_str(i)))
        else:
          self.x_log("We called {}{} and it returned an INCORRECT result: {}".format(name, arglist_str(i), str(hw_func_result)))
          self.i_log("We called {}{} and it returned an INCORRECT result: {}".format(name, arglist_str(i), str(hw_func_result)))
          fail = True
          return False
          # break      
      else:
          priv_count = 0
          if not fail:
              hw_func_result = hw_func(*i_copy1)
              if the_same(hw_func_result,ta_func(*i_copy2)):
                priv_count += 1
                self.i_log("We called {} on a hidden input and it returned the correct result.".format(name))
                self.x_log("We called {} on a hidden input and it returned the correct result.".format(name))
              else:
                self.i_log("We called {} on a hidden input and it returned the correct result.".format(name))
                self.x_log("We called {} on a hidden input and it returned an INCORRECT result.".format(name))
                return False
                
           
    except Exception as e:
      self.x_log("Exception raised while running tests on {!s}. Try testing to see if you can recreate the exception and solve it.".format(name))
      self.i_log("Exception raised... hopefuly not our fault.")
      print(e)
      return False
    return True


  def compare_logs(self, student_output, ta_output, inputs, private):
    success = False  
    ins = ', '.join([repr(inp) for inp in inputs])
    #ins = repr(inputs[0])
    #for s in inputs[1:]:
    #    ins = ins + ", " + repr(s)    
    if not private:
        if student_output == None:
            self.x_log("An error occurred running your script with input "+ins+".")
        elif student_output != ta_output:
            self.x_log("Incorrect output with input "+ins+".") 
            if len(student_output) > 0 and student_output[-1] != "\n":
                self.x_log("Your output is missing a final end-of-line character.")
            else:
                st_lines = len(student_output.split("\n"))-1
                ta_lines = len(ta_output.split("\n"))-1
                if st_lines != ta_lines:
                    self.x_log("Your transcript had "+str(st_lines)+" lines.")
                    self.x_log("Our transcript had "+str(ta_lines)+" lines.")
                self.x_log("----- Your script produced:")
                self.x_log_all(student_output)
                self.x_log("----- The solution script produced:")
                self.x_log_all(ta_output)
                self.x_log("-----")
        else:
            success = True
            self.x_log("Test with input "+ins+" PASSED!")
    else:
        if student_output == None:
            self.x_log("An error occurred running your script during one of our tests.")
        elif student_output != ta_output:
            self.x_log("Incorrect output with one of our test inputs.")
            if len(student_output) == 0 and student_output[-1] != "\n":
                self.x_log("Your output is missing a final end-of-line character.")
        else:
            success = True
            self.x_log("Test on hidden input PASSED!")    
    if success:
        self.i_log("code on "+ins+" SUCCEEDED.")
    else:
        self.i_log("code on "+ins+" FAILED.")
    return success


  def _arg_compare(self, ta_obj, hw_obj):
    '''
    _arg_compare() takes two objec
    '''
    log = []
    ta_funcs = set(listfunction_names(ta_obj))
    hw_funcs = set(listfunction_names(hw_obj))
    ta_farg = {f:getfunction_argcount(ta_obj, f) for f in ta_funcs}
    hw_farg = {f:getfunction_argcount(hw_obj, f) for f in hw_funcs}
    args_there = True #innocent until proven guilty

    for func, arg_count in ta_farg.items():
      hw_arg_count = hw_farg[func]
      if arg_count == hw_arg_count:
        log.append("PASSED@{!s}: {!r} args defined in ta-{!s}. {!r} args in submitted-{!s}".format(func, arg_count, ta_obj.__name__ + "." + func, hw_arg_count, hw_obj.__name__ + "." + func))
      else: 
        log.append("ERROR@{!s}: {!r} args defined in ta-{!s}. {!r} args in submitted-{!s}".format(func, arg_count, ta_obj.__name__ + "." + func, hw_arg_count, hw_obj.__name__ + "." + func))
        self.x_log("You defined {!r} args in submitted-{!s}, there should be {!r} argument(s)".format(hw_arg_count, hw_obj.__name__ + "." + func, arg_count))
        args_there = False
    return args_there, log


  def compare(self):
    '''
     compare() does a basic comparison of two modules (or objects), checking to make sure that all functions and classes
     are defined with the appropriate number of arguments. returns true if so, false otherwise.
    ''' 

    all_there = True #innocent until proven guilty
    ta_module = self.ta_obj
    hw_module = self.hw_obj

    #scrape functions from top level:
    ta_top_lvl = set(listfunction_names(ta_module))
    hw_top_lvl = set(listfunction_names(hw_module))
    if ta_top_lvl <= hw_top_lvl:
      all_there, log = self._arg_compare(ta_module, hw_module)
      self._clog("top_lvl_funcs", log)
    else:
      #also log the missing ones
      missing = ta_top_lvl - hw_top_lvl
      missing_str = ", ".join(str(e) for e in missing)
      self._clog("top_lvl_funcs", "ERROR: some top level function(s) defined in ta-{!s} are missing in submitted-{!s}: {!s}".format(ta_module.__name__, hw_module.__name__, missing_str))
      self.x_log("{!s}.py is missing the following functions: {!s}".format(hw_module.__name__, missing_str))
      all_there = False

    #scrape classes from TA_file, hw_file, and compare them
    hw_class_dict = getclass_dict(hw_module)
    ta_class_dict = getclass_dict(ta_module)
    ta_class_names = set(ta_class_dict.keys())
    hw_class_names = set(hw_class_dict.keys())
    common_class_names = ta_class_names & hw_class_names

    #high level check to make sure all the classes in TA_module are defined in hw_module (no check to see if there's extra stuff defined in hw_module)
    if ta_class_names <= hw_class_names:
      self._clog("classes", "PASSED: all the classes in ta-{!s} exist in {!s}".format(ta_module.__name__, hw_module.__name__))

    else:
      missing = ta_class_names - hw_class_names
      missing_str = ", ".join(str(e) for e in missing)
      self._clog("classes", "ERROR: some classes defined in ta-{!s} are missing from submitted-{!s}: {!s}".format(ta_module.__name__, hw_module.__name__, missing_str))
      self.x_log("{!s}.py is missing the following classes: {!s}".format(hw_module.__name__, missing_str))
      all_there = False

    #scrape functions from the common classes:
    for cls_name in common_class_names:
      hw_cls = hw_class_dict[cls_name]
      ta_cls = ta_class_dict[cls_name]
      ta_cls_funcs = set(listfunction_names(ta_cls))
      hw_cls_funcs = set(listfunction_names(hw_cls))
      cls_func_compare = str(cls_name)+"_funcs"
      if ta_cls_funcs <= hw_cls_funcs:
        cls_args_there, log = self._arg_compare(ta_cls, hw_cls)
        self._clog(cls_func_compare, log)
        if all_there and not cls_args_there:
          all_there = False
      else:
        missing = ta_cls_funcs - hw_cls_funcs
        missing_str = ", ".join(str(e) for e in missing)
        self._clog(cls_func_compare, "ERROR: some functions defined in ta-{!s}'s class {!s} are missing from submitted-{!s}'s class {!s}: {!s}".format(ta_module.__name__, cls_name, hw_module.__name__, cls_name, missing_str))
        self.x_log("Your class {!s} is missing some functions: {!s}".format(hw_module.__name__ +"." + cls_name, missing_str))
        all_there = False

    return all_there



  def _load_data(self):
    '''.
    used internally: _load_data(): grabs the small json object passed in
    '''
    submission_data = self.DATA_DIR + self.DATA_FILE
    try:
        with open(submission_data) as data_file: 
            self.data = json.load(data_file)
    except FileNotFoundError:
        self.data = { "attempts": 1, "prevscore": 0, "timedelta": 0 }

  def get_attempts(self):
    '''
    get_attempts returns the number of attempts on this problem / problem set
    '''
    attempts = self.data['attempts']
    return attempts

  def get_timedelta(self):
    '''
    gettimedelta returns the 0(on time) or -1 (late) on this problem / problem set, just a placeholder for now
    '''
    timedelta = self.data['timedelta']
    return timedelta

  def get_prevscore(self):
    '''
    get_prevscore returns the previous score (if any, one this problem)
    '''
    prevscore = self.data['prevscore']
    return prevscore

  def _info(self, key, message):
    '''
    used internally: _info logs to the 'info' key of the session log, 
    contains data about the session object
    '''
    self.log["info"][key] = message

  def _clog(self, key, message):
    '''
    used internally: _clog logs to the 'sanity_compare' key of the session log
    can be accessed by the TA
    '''
    # if key not in self.log["sanity_compare"]:
    #   self.log["sanity_compare"][key] = []
    # self.log["sanity_compare"][key].append(message) 
    self.log["sanity_compare"][key] = message

  def i_log(self, message):
    '''
    for external use: logs to the internal portion of the session log, 
    anything logged here is saved to the database for the TA's reference
    '''
    self.log["internal_log"].append(message)

  def i_log_all(self, messages):
    '''
    for external use: logs to the internal portion of the session log,
    anything logged here is saved to the database for the TA's reference
    '''
    for message in messages.split("\n"):
      self.i_log(message)

  def x_log(self, message):
    '''
    for external use: logs to the external portion of the session log,
    anything logged here is passed back to the student
    '''
    self.log["external_log"].append(message)

  def x_log_all(self, messages):
    '''
    for external use: logs to the external portion of the session log,
    anything logged here is passed back to the student
    '''
    for message in messages.split("\n"):
      self.x_log(message)

  def set_max_score(self, max_score):
    '''sets the max score for the problem'''
    self._maxscore = max_score

  def set_score(self, new_score):
    ''' sets the new score for the homework '''
    # self.log["score_sum"].append("score set: {!r}")
    self._score = new_score

  def get_score(self):
    '''returns the current score'''
    return self._score

  def update_score(self, score_mod):
    ''' changes the value of self._score by the (int) given '''
    self._score += score_mod

  def finalize(self):
    '''
    for external use: finalize computes the final score (using the values of the score key)
    and logs the start & end times of the session, along with some data about the problem set
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
     
  def tab_report(self):
    if find_tabs(self.hw_obj):
      self.x_log("It looks like you are using tabs in your source code. You should configure your editor so it changes tabs to spaces.")

    
class DeadSession(Session):

    def __init__(self):
        Session.__init__(self, None, None)

    def compare(self):
        return True
    
    def test_hw_function(self, name, pub_inputs, priv_inputs, the_same=(lambda x,y: x == y)):
        return False
