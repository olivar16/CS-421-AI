  # -*- coding: latin-1 -*-
import random
from Player import *
from Constants import *
from Construction import CONSTR_STATS
from Ant import UNIT_STATS
from Move import Move
from GameState import addCoords
from AIPlayerUtils import *

#Globally access coordinates for anthill and tunnel
anthill = (0,0)
tunnel = (0,1)
#Store the locations of the food placed on the enemy side
foodLocs = []

##
#AIPlayer
#Description: The responsbility of this class is to interact with the game by
#deciding a valid move based on a given game state. This class has methods that
#will be implemented by students in Dr. Nuxoll's AI course.
#
#Variables:
#   playerId - The id of the player.
##
class AIPlayer (Player):

    #__init__
    #Description: Creates a new Player
    #
    #Parameters:
    #   inputPlayerId - The id to give the new player (int)
    ##
    def __init__(self, inputPlayerId):
        super(AIPlayer,self).__init__(inputPlayerId, "Paul and Morgan's AI")
    
    
    
    ##
    #getPlacement
    #Description: The getPlacement method corresponds to the 
    #action taken on setup phase 1 and setup phase 2 of the game. 
    #In setup phase 1, the AI player will be passed a copy of the 
    #state as currentState which contains the board, accessed via 
    #currentState.board. The player will then return a list of 10 tuple 
    #coordinates (from their side of the board) that represent Locations 
    #to place the anthill and 9 grass pieces. In setup phase 2, the player 
    #will again be passed the state and needs to return a list of 2 tuple
    #coordinates (on their opponent�s side of the board) which represent
    #Locations to place the food sources. This is all that is necessary to 
    #complete the setup phases.
    #
    #Parameters:
    #   currentState - The current state of the game at the time the Game is 
    #       requesting a placement from the player.(GameState)
    #
    #Return: If setup phase 1: list of ten 2-tuples of ints -> [(x1,y1), (x2,y2),�,(x10,y10)]
    #       If setup phase 2: list of two 2-tuples of ints -> [(x1,y1), (x2,y2)]
    ##
    def getPlacement(self, currentState):
        global anthill
        global tunnel
        global foodLocs
        anthill = (0,0)
        tunnel = (4,3)
        numToPlace=0
        #Place anthill at the back of the gameboard.
        #Place tunnel along the border to provide shortest path for worker ants
        #Place grass along the border to slow down enemy on the front lines
        if currentState.phase == SETUP_PHASE_1:
            numToPlace=11
            moves=[anthill, tunnel, (9,3), (8,3), (7,3), (6,3), (5,3), (2,2), (0,3), (2,3), (1,3)]
            return moves
        elif currentState.phase == SETUP_PHASE_2:
            numToPlace=2
            moves=[]
            foodLocs = []
            for i in range(0, numToPlace):
                move=None
                while move == None:
                    #Try to place food towards the front of enemy lines, starting from the bottom right
                    for y in range(6,8):
                        for x in range(0,10):
                            if currentState.board[x][y].constr == None and (x,y) not in moves:
                                move = (x,y)
                                foodLocs.append(move)
                                currentState.board[x][y].constr == True
                                break
                        if move != None:
                            break     
                moves.append(move)
            return moves
        else:
            return [(0,0)]
    
    ##
    #getMove
    #Description: The getMove method corresponds to the play phase of the game 
    #and requests from the player a Move object. All types are symbolic 
    #constants which can be referred to in Constants.py. The move object has a 
    #field for type (moveType) as well as field for relevant coordinate 
    #information (coordList). If for instance the player wishes to move an ant, 
    #they simply return a Move object where the type field is the MOVE_ANT constant 
    #and the coordList contains a listing of valid locations starting with an Ant 
    #and containing only unoccupied spaces thereafter. A build is similar to a move 
    #except the type is set as BUILD, a buildType is given, and a single coordinate 
    #is in the list representing the build location. For an end turn, no coordinates 
    #are necessary, just set the type as END and return.
    #
    #Parameters:
    #   currentState - The current state of the game at the time the Game is 
    #       requesting a move from the player.(GameState)   
    #
    #Return: Move(moveType [int], coordList [list of 2-tuples of ints], buildType [int])
    ##
    def getMove(self, currentState):
      
        #Generate a random move for any ants that are not commanded
        moves = listAllLegalMoves(currentState)
        randMove = moves[random.randint(0,len(moves) - 1)]
        
        #Get a list of all possible build moves
        buildMoves = listAllBuildMoves(currentState)
        
        #Once 2 workers have been built, start building drones
        for build in buildMoves:
            if (build.buildType==DRONE):
                return build
            elif build.buildType==WORKER and len(getAntList(currentState, PLAYER_TWO, (WORKER,)))<2:
                return build

          
                
        
        #Tell all worker ants to pursue the nearest food source
        workerants = getAntList(currentState, PLAYER_TWO, (WORKER,))
        for worker in workerants:
             if worker.hasMoved == False:
                 if worker.carrying == False:
                    moves = listAllMovementPaths(currentState, worker.coords, UNIT_STATS[worker.type][MOVEMENT])
                    nearestFoodCoord = None
                    finalMoveCoords = None
                    #Find nearest food source
                    if stepsToReach(currentState, worker.coords, foodLocs[0]) < stepsToReach(currentState, worker.coords, foodLocs[1]):
                        nearestFoodCoord = foodLocs[0]
                    else:
                        nearestFoodCoord = foodLocs[1]
                       
                    #Find the move that brings you closest to the food source
                    for index in range(0, len(moves)):
                        if index is not 0:
                            prevLength = len(finalMoveCoords)
                            currLength = len(moves[index])
                            if stepsToReach(currentState,finalMoveCoords[prevLength-1], nearestFoodCoord) > stepsToReach(currentState,moves[index][currLength-1], nearestFoodCoord):
                                finalMoveCoords = moves[index]               
                        else:
                           finalMoveCoords = moves[0]
                  
                    finalMoveObj = Move(MOVE_ANT, finalMoveCoords, 0)
                    return finalMoveObj
                 else:
                    moves = listAllMovementPaths(currentState, worker.coords, UNIT_STATS[worker.type][MOVEMENT])
                    finalMoveCoords = None
                    #Find the move that brings you closest to the anthill
                    for index in range(0, len(moves)):
                        if index is not 0:
                            prevLength = len(finalMoveCoords)
                            currLength = len(moves[index])
                            if stepsToReach(currentState,finalMoveCoords[prevLength-1], tunnel) > stepsToReach(currentState,moves[index][currLength-1], tunnel):
                                finalMoveCoords = moves[index]               
                        else:
                            finalMoveCoords = moves[0]
                 finalMoveObj = Move(MOVE_ANT, finalMoveCoords, 0)
                 return finalMoveObj
        
        #Command drones to zerg QUEEN
        attackants = getAntList(currentState, PLAYER_TWO, (DRONE,))
        #Get the location of the queen
        enemyQueen = getAntList(currentState, PLAYER_ONE, (QUEEN,))[0]
        queenLocation = enemyQueen.coords
        finalMoveCoords=None
        #Let all attack ants go toward the queen
        for attacker in attackants:
            if attacker.hasMoved == False:
                moves = listAllMovementPaths(currentState, attacker.coords, UNIT_STATS[attacker.type][MOVEMENT])
                for index in range(0, len(moves)):
                    if index is not 0:
                        prevLength = len(finalMoveCoords)
                        currLength = len(moves[index])
                        if stepsToReach(currentState,finalMoveCoords[prevLength-1], queenLocation) > stepsToReach(currentState,moves[index][currLength-1], queenLocation):
                                finalMoveCoords = moves[index]               
                    else:                                      
                        finalMoveCoords = moves[0]
                finalMoveObj = Move(MOVE_ANT, finalMoveCoords, 0)
                return finalMoveObj        
                
        #Any unspecified ants will have a random move
        return randMove
    
    ##
    #getAttack
    #Description: The getAttack method is called on the player whenever an ant completes 
    #a move and has a valid attack. It is assumed that an attack will always be made 
    #because there is no strategic advantage from withholding an attack. The AIPlayer 
    #is passed a copy of the state which again contains the board and also a clone of 
    #the attacking ant. The player is also passed a list of coordinate tuples which 
    #represent valid locations for attack. Hint: a random AI can simply return one of 
    #these coordinates for a valid attack. 
    #
    #Parameters:
    #   currentState - The current state of the game at the time the Game is requesting 
    #       a move from the player. (GameState)
    #   attackingAnt - A clone of the ant currently making the attack. (Ant)
    #   enemyLocation - A list of coordinate locations for valid attacks (i.e. 
    #       enemies within range) ([list of 2-tuples of ints])
    #
    #Return: A coordinate that matches one of the entries of enemyLocations. ((int,int))
    ##
    def getAttack(self, currentState, attackingAnt, enemyLocations):       
        return enemyLocations[random.randint(0, len(enemyLocations) - 1)]
       
        
    ##
    #registerWin
    #Description: The last method, registerWin, is called when the game ends and simply 
    #indicates to the AI whether it has won or lost the game. This is to help with 
    #learning algorithms to develop more successful strategies.
    #
    #Parameters:
    #   hasWon - True if the player has won the game, False if the player lost. (Boolean)
    #
    def registerWin(self, hasWon):
        #method templaste, not implemented
        pass
