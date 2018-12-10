"""
import json
import datetime
import inspect


class Session():
    '''
    Session object: a session object takes in two modules (a key, or solution module, and a submission module)
    it stores the results of the compare() function and maintains various logs and score information
    '''
    def __init__(self):
        self.start_time = datetime.datetime.now().strftime(
                "%A, %d. %B %Y %I:%M:%S%p")
        self.DATA_DIR = ''
        self.DATA_FILE = 'data.json'
        self.log = {"info":{}, 
                    "internal_log":[], 
                    "external_log":[], 
                    "score_sum": None, 
                    "max_score": None}
        submission_data = self.DATA_DIR + self.DATA_FILE
        try:
            with open(submission_data) as data_file: 
                self.data = json.load(data_file)
        except FileNotFoundError:
            self.data = { "attempts": 1, "prevscore": 0, "timedelta": 0 }
    
    def notify(self, test_result, test):
        if test.private():
            self.x_log("Running on a hidden test.")
        else:
            self.x_log("Running test: {}".format(str(test)))
        self.x_log(str(test_result))


    def get_attempts(self):
        '''
        get_attempts returns the number of attempts on this problem / problem set
        '''
        attempts = self.data['attempts']
        return attempts

    def get_timedelta(self):
        '''
        gettimedelta returns the 0(on time) or -1 (late) on this 
        problem / problem set, just a placeholder for now
        
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

    def update_score(self, score_mod):
        ''' changes the value of self._score by the (int) given '''
        self._score += score_mod

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

 """