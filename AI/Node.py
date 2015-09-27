__author__ = 'Ryson Asuncion and Casey Sigelmann'

class Node():

    def __init__(self, initMove, potentialState, initParentNode, initEvaluation):
        self.move = initMove
        self.state = potentialState
        self.parentNode = initParentNode
        self.evaluation = initEvaluation
