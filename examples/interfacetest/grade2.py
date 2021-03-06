from autograder import Autograder, InterfaceTest
pub_inputs = [('DrawDominoSet()',), 
              ('Domino(3,5).getLeftDots()',), 
              ('Domino(3,5).getRightDots()',)]
pub_outputs = [
        """0-0 0-1 0-2 0-3 0-4 0-5 0-6
        1-1 1-2 1-3 1-4 1-5 1-6
        2-2 2-3 2-4 2-5 2-6
        3-3 3-4 3-5 3-6
        4-4 4-5 4-6
        5-5 5-6
        6-6""", 
        "3", 
        "5"]
priv_inputs = [] 
priv_outputs = []
tests = InterfaceTest.create_batch("client2", "DominoClient", 
                                   pub_inputs, pub_outputs, 
                                   priv_inputs, priv_outputs)
Autograder().run(tests)
