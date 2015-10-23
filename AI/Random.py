import random
from Player import *
from Constants import *
from Construction import CONSTR_STATS
from Ant import UNIT_STATS
from Move import Move
from GameState import addCoords
from AIPlayerUtils import *

##
#AIPlayer
#Description: The responsbility of this class is to interact with the game by
#deciding a valid move based on a given game state. This class has methods that
#will be implemented by students in Dr. Nuxoll's AI course.
#
#Variables:
#   playerId - The id of the player.
##
class AIPlayer(Player):

    #__init__
    #Description: Creates a new Player
    #
    #Parameters:
    #   inputPlayerId - The id to give the new player (int)
    ##
    def __init__(self, inputPlayerId):
        super(AIPlayer,self).__init__(inputPlayerId, "Random BFS")
    
    ##
    #getPlacement
    #
    #Description: called during setup phase for each Construction that
    #   must be placed by the player.  These items are: 1 Anthill on
    #   the player's side; 1 tunnel on player's side; 9 grass on the
    #   player's side; and 2 food on the enemy's side.
    #
    #Parameters:
    #   construction - the Construction to be placed.
    #   currentState - the state of the game at this point in time.
    #
    #Return: The coordinates of where the construction is to be placed
    ##
    def getPlacement(self, currentState):
        numToPlace = 0
        #implemented by students to return their next move
        if currentState.phase == SETUP_PHASE_1:    #stuff on my side
            numToPlace = 11
            moves = []
            for i in range(0, numToPlace):
                move = None
                while move == None:
                    
                    
                    #Choose any x location
                    x = random.randint(0, 9)
                    
                    #Choose any y location on your side of the board
                    y = random.randint(0, 3)
                    
                    #Set the move if this space is empty
                    if currentState.board[x][y].constr == None and (x, y) not in moves:
                        move = (x, y)
                        print "Figure " + str(i) + " placed in " + str(x) + " " +  str(y)
                        #Just need to make the space non-empty. So I threw whatever I felt like in there.
                        currentState.board[x][y].constr == True
                moves.append(move)
            return moves
        elif currentState.phase == SETUP_PHASE_2:   #stuff on foe's side
            numToPlace = 2
            moves = []
            for i in range(0, numToPlace):
                move = None
                while move == None:
                    #Choose any x location
                    x = random.randint(0, 9)
                    #Choose any y location on enemy side of the board
                    y = random.randint(6, 9)
                    #Set the move if this space is empty
                    if currentState.board[x][y].constr == None and (x, y) not in moves:
                        move = (x, y)
                        #Just need to make the space non-empty. So I threw whatever I felt like in there.
                        currentState.board[x][y].constr == True
                moves.append(move)
            return moves
        else:
            return [(0, 0)]
    
    ##
    #getMove
    #Description: Gets the next move from the Player.
    #
    #Parameters:
    #   currentState - The state of the current game waiting for the player's move (GameState)
    #
    #Return: The Move to be made
    ##
    def getMove(self, currentState):
        moves = listAllLegalMoves(currentState)
       # Move(moveType [int], coordList [list of 2-tuples of ints], buildType [int])
        
        move = moves[random.randint(0,len(moves) - 1)]
        
        if move.moveType == MOVE_ANT:
            ant = getAntAt(currentState, move.coordList[0])
            self.checkState(currentState, move)
        print "Move completed" 
        return move
    
    ##
    #getAttack
    #Description: Gets the attack to be made from the Player
    #
    #Parameters:
    #   currentState - A clone of the current state (GameState)
    #   attackingAnt - The ant currently making the attack (Ant)
    #   enemyLocation - The Locations of the Enemies that can be attacked (Location[])
    ##
    def getAttack(self, currentState, attackingAnt, enemyLocations):
        #Attack a random enemy.
        return enemyLocations[random.randint(0, len(enemyLocations) - 1)]
        

    ##
    #checkState
    #Description: Determines what the agent's state would look like after a given move
    #
    #Parameters:
    # currentState - A clone of the curent state (GameState)
    # move - An instance of the move class (Move)
    #
    #Return: newState - A clone of a GameState that is modified with the move result
    ##
    def checkState(self, currentState, move):
        #Get the move type of the given move
        modifiedState = currentState.clone()
        print "The move is " + str(move)
        #If you want to move ant, get the coordinates of where to move
        if (move.moveType == MOVE_ANT):
            moveCoords = move.coordList
            #Find start coord and end coord
            currCoord = move.coordList[0]
            endCoord = move.coordList[-1]
            #get ant to move
            antToMove = modifiedState.board[currCoord[0]][currCoord[1]].ant
            print "Ant is of type " + str(antToMove.type)
            print "Moving ant FROM: " + str(antToMove.coords)
            movePoints = UNIT_STATS[antToMove.type][MOVEMENT]             
            previousCoord = None
            antToMove.coords=(endCoord[0], endCoord[1])
            print "TO: " + str(antToMove.coords)
            antToMove.hasMoved = True
            #Remove ant from location
            modifiedState.board[currCoord[0]][currCoord[1]].ant = None
            #put ant at last loc in coordList
            modifiedState.board[endCoord[0]][endCoord[1]].ant = antToMove
            #If ant is worker, and is on top of food, then pick it up
            if(antToMove.type==WORKER):
                constr = getConstrAt(modifiedState, antToMove.coords)
                if (constr != None):
                    if constr.type == FOOD:
                        
                        antToMove.carrying=True
                    elif (constr.type == ANTHILL) or (constr.type == TUNNEL):
                      
                        modifiedState.inventories[antToMove.player].foodCount+=1
                       
                        antToMove.carrying=False
            
            adjTiles = listReachableAdjacent(modifiedState, endCoord, movePoints)
            #Iterate through all adjacent tiles. If there's an ant, attack it
            for tile in adjTiles:
                ant = getAntAt(modifiedState, tile)
                if ant is not None:
                    ant.health-=1
                    break
                    
                    
            return modifiedState
            
            
        #If move type is build, then get what to build
        elif (move.moveType == BUILD):
            buildType = move.buildType
            
        elif (move.moveType == END):
            return currentState    
            
        #Create a clone of a GameState
        
        #Modify state to the move
        
        
        print "Testing case"
        board = [[Location((col, row)) for row in xrange(0,BOARD_LENGTH)] for col in xrange(0,BOARD_LENGTH)]
        state = GameState(board, [p1Inventory, p2Inventory, neutralInventory], MENU_PHASE, PLAYER_ONE)
        player = AIPlayer(PLAYER_ONE)
        move = (MOVE_ANT, coordList [(0,0), (0,1), (0,2)], 0)
        checkState(state, move)