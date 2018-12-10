import inspect
from util import InterfaceDiscrepancy, CorrectResult

def listfunction_names(obj):
  '''
  listfunction_names takes an object(e.g: module, class) and returns an array of the function names (strings)
  ''' 
  all_functions = inspect.getmembers(obj, inspect.isfunction)
  names = [x[0] for x in all_functions]
  return names


def arg_compare(ta_obj, hw_obj):
    """
    Determines whether the arguments of two methods are the same.

    """    

    def getfunction_argcount(obj, function_name):
        '''
        getfunction_argcount returns the number of args in a function
        '''
        f = getattr(obj, function_name)
        arg_count = f.__code__.co_argcount
        return arg_count


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
        args_there = False
    return args_there, '\n'.join(log)


def compare(ta_module, hw_module):
    """
     compare() does a basic comparison of two modules (or objects), checking to make sure that all functions and classes
     are defined with the appropriate number of arguments. returns true if so, false otherwise.
    
    """ 
    def getclass_dict(module):
        '''
        getclass_dict takes a module and returns a dict of {(className:classObject), (...)}
        ''' 
        all_classes = inspect.getmembers(module, inspect.isclass)
        classes = {x[0]:x[1] for x in all_classes}
        return classes

    all_there = True #innocent until proven guilty

    result_log = ""

    #scrape functions from top level:
    ta_top_lvl = set(listfunction_names(ta_module))
    hw_top_lvl = set(listfunction_names(hw_module))
    if ta_top_lvl <= hw_top_lvl:
      all_there, log = arg_compare(ta_module, hw_module)
    else:
      #also log the missing ones
      missing = ta_top_lvl - hw_top_lvl
      missing_str = ", ".join(str(e) for e in missing)
      log = "{!s}.py is missing the following functions: {!s}".format(hw_module.__name__, missing_str)
      all_there = False
    result_log += log

    #scrape classes from TA_file, hw_file, and compare them
    hw_class_dict = getclass_dict(hw_module)
    ta_class_dict = getclass_dict(ta_module)
    ta_class_names = set(ta_class_dict.keys())
    hw_class_names = set(hw_class_dict.keys())
    common_class_names = ta_class_names & hw_class_names

    #high level check to make sure all the classes in TA_module are defined in hw_module (no check to see if there's extra stuff defined in hw_module)
    if ta_class_names > hw_class_names:
      missing = ta_class_names - hw_class_names
      missing_str = ", ".join(str(e) for e in missing)
      result_log += "\n{!s}.py is missing the following classes: {!s}".format(hw_module.__name__, missing_str)
      all_there = False

    #scrape functions from the common classes:
    for cls_name in common_class_names:
      hw_cls = hw_class_dict[cls_name]
      ta_cls = ta_class_dict[cls_name]
      ta_cls_funcs = set(listfunction_names(ta_cls))
      hw_cls_funcs = set(listfunction_names(hw_cls))
      if ta_cls_funcs <= hw_cls_funcs:
        cls_args_there, log = arg_compare(ta_cls, hw_cls)
        if all_there and not cls_args_there:
          all_there = False
      else:
        missing = ta_cls_funcs - hw_cls_funcs
        missing_str = ", ".join(str(e) for e in missing)
        result_log += "Your class {!s} is missing some functions: {!s}".format(hw_module.__name__ +"." + cls_name, missing_str)
        all_there = False

    if not all_there:
        return InterfaceDiscrepancy(result_log)
    else:
        return CorrectResult()