import random
import sys
from Building import Building
from Inventory import Inventory
from Location import Location
from Player import *
from Constants import *
from Construction import CONSTR_STATS
from Ant import UNIT_STATS, Ant
from Move import Move
from GameState import addCoords, GameState
from AIPlayerUtils import *
from decimal import Decimal

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
        super(AIPlayer,self).__init__(inputPlayerId, "Simple BFS (Kirk and Paul)")
        self.DEPTH_LIMIT = 1

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
        bestScore = -10.0  #Ensure a move is commited
        bestMove = None
        for move in moves:
            #self.checkState(currentState, move),
            score = self.evaluateState(self.checkState(currentState, move),currentState)
            if (score > bestScore):
                bestScore = score
                bestMove = move

        return bestMove



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
        #Clone state
        modifiedState = currentState.fastclone()

        ants = modifiedState.inventories[self.playerId].ants

        if move.moveType == MOVE_ANT:
            #Get ant and update location
            startingCoord = move.coordList[0]
            for candidateAnt in ants:
                if candidateAnt.coords == startingCoord:
                    ant = candidateAnt

            ant.coords = move.coordList[-1]

            #Allow worker ants to pick up and drop off food
            if ant.type == WORKER:
                constr = getConstrAt(modifiedState, ant.coords)
                #Let ant perform actions based on the construction that it's on
                if constr is not None:
                    if constr.type == FOOD:
                        ant.carrying = True
                    elif ((constr.type == ANTHILL) or (constr.type == TUNNEL)) and ant.carrying:
                        modifiedState.inventories[self.playerId].foodCount += 1
                        ant.carrying = False

            #Resolve attacks
            opponentId = (modifiedState.whoseTurn + 1) % 2
            range = UNIT_STATS[ant.type][RANGE]
            #Find an enemy ant that is within range of the current ant
            for enemyAnt in modifiedState.inventories[opponentId].ants:
                #Check if the attack is valid
                diffX = abs(ant.coords[0] - enemyAnt.coords[0])
                diffY = abs(ant.coords[1] - enemyAnt.coords[1])
                #if attacking ant is within range of enemy ant, attack
                if range ** 2 >= diffX ** 2 + diffY ** 2:
                    enemyAnt.health -= 1
                    if enemyAnt.health == 0:
                        modifiedState.inventories[opponentId].ants.remove(enemyAnt)
                    break

        #If move type is build, then get what to build
        elif move.moveType == BUILD:
            coord = move.coordList[0]
            currentPlayerInv = modifiedState.inventories[self.playerId]
            #subtract the cost of the item from the player's food count
            if move.buildType == TUNNEL:
                currentPlayerInv.foodCount -= CONSTR_STATS[move.buildType][BUILD_COST]
                currentPlayerInv.constrs.append(Building(coord, TUNNEL, modifiedState.whoseTurn))
            else:
                currentPlayerInv.foodCount -= UNIT_STATS[move.buildType][COST]
                ant = Ant(coord, move.buildType, modifiedState.whoseTurn)
                currentPlayerInv.ants.append(ant)
                ant.hasMoved = True

        return modifiedState


    
    ##
    #evaluateState
    #Description: Given a state returns a double between 0 and 1 depending on the metics given
    #
    #Parameters:
    # gameState - A clone of the curent state (GameState)
    # trueState - The actual state of gamestate to tell if the ant is currently carrying grapes
    #
    #Return: score - A double representing how effective the state is
    ##
    def evaluateState(self, gameState, trueState):
        #Get player's ants
        agentAnts = gameState.inventories[self.playerId].ants
        opponentId = (gameState.whoseTurn + 1) % 2

        #Check if player has won
        if (gameState.inventories[opponentId].getQueen() is None):
            print "Enemy queen dead"
            return 1.0
        if (gameState.inventories[self.playerId].foodCount >= 11):
            print "Food count more than 11"
            return 1.0

        #Check if player has lost
        if (gameState.inventories[self.playerId].getQueen() is None):
            return 0.0
        if (gameState.inventories[opponentId].foodCount >= 11):
            return 0.0

        #init score
        score = 0.5

        tunnelCoord = getConstrList(gameState, self.playerId, [(TUNNEL)])[0].coords
        foodTuple = getConstrList(gameState, None, [(FOOD)])
        #Praise ant for being close to a target
        antIndex = 0
        for ant in trueState.inventories[self.playerId].ants:
            if ant.type is QUEEN:
                antIndex += 1
                continue

            if ant.carrying:
                realTunnelDistance = stepsToReach(trueState, ant.coords, tunnelCoord)
                potentialTunnelDistance = stepsToReach(gameState, gameState.inventories[self.playerId].ants[antIndex].coords, tunnelCoord)
                if realTunnelDistance > potentialTunnelDistance:
                    score += 0.3
                else:
                    score -= 0.2

            elif not ant.carrying:
                grape = foodTuple[0].coords
                realGrapeDistance = stepsToReach(trueState, ant.coords, grape)
                potentialGrapeDistance = stepsToReach(gameState, gameState.inventories[self.playerId].ants[antIndex].coords, grape)
                if realGrapeDistance > potentialGrapeDistance:
                    score += 0.3
                else:
                    score -= 0.2
            antIndex += 1

        #Rate food count
        enemyFood = gameState.inventories[opponentId].foodCount
        agentFood = gameState.inventories[self.playerId].foodCount
        if agentFood > enemyFood:
            score += 0.05
        elif agentFood < enemyFood:
            score -= 0.05

        #Rate the carrying count
        for ant in agentAnts:
            if (ant.carrying == True):
                score += 0.04

        #Rate number of ants
        antCount = len(agentAnts)
        if (antCount > 2 and antCount < 5):
            score += 0.03
        else:
            score -= 0.02
        return score
    
    ##
    #evaluateNodes
    #Description: Evaluates a list of nodes
    #
    #Parameters:
    #nodeList - A list of Node objects
    #
    #Return: score - A double representing how effective the state is (double)
    ##
    def evaluateNodes(nodeList):
        avgEval = 0.0
        for node in nodeList:
            avgEval += node.stateEval
        avgEval = (avgEval)/(len(nodeList))
    
    ##
    #searchTree
    #Description: Explore the search tree to find the best move
    #
    #Parameters:
    # currentState - The current state of the game (GameState)
    # PID - The agent's player id (int)
    # currentDepth - An int that denotes the current depth of the given state in the tree (int) 
    #
    #Return: bestResult - A tuple containing the move that leads to the best branch
    #                     in the tree along with a score indicating how good it is
    ## 
    def searchTree(currentState, PID, currentDepth):
        
        #Base case: currentDepth is equal to the depth DEPTH_LIMIT
        if (currentDepth == self.DEPTH_LIMIT):
            print "Base case"
        
        #Create a node for each state that could be reached from the current state
    
    
      
    ##
    #Node
    #Description: A class used to represent a node in a search tree
    #
    #Variables:
    #   move - the Move that would be taken in the given state from the parent node
    #   reachState - the state that would be reached by taking that move
    #   stateEval - an evaluation of this state. 
    #   parentNode - Reference to parent node
    ##
    class Node:
        def __init__(self, move, reachState, stateEval, parentNode):
            self.move = move
            self.reachState = reachState
            self.stateEval = stateEval
            self.parentNode = parentNode
               
#UNIT TEST
print "TEST CASE #1"
#Prepare a demo board to build gameState
p1Inventory = Inventory(PLAYER_ONE, [], [], 0)
p2Inventory = Inventory(PLAYER_TWO, [], [], 0)
neutralInventory = Inventory(NEUTRAL, [], [], 0)
board = [[Location((col, row)) for row in xrange(0,BOARD_LENGTH)] for col in xrange(0,BOARD_LENGTH)]
sampAnt = Ant((0,0), WORKER, PLAYER_ONE)
enemyAnt = Ant((3,4), WORKER, PLAYER_TWO)
enemyQueen = Ant((6,4), QUEEN, PLAYER_TWO)
playerOneQueen = Ant((7,5), QUEEN, PLAYER_ONE)

#Food ant that's already carrying something
foodAnt = Ant((4,4), WORKER, PLAYER_ONE)
foodAnt.carrying = True
sampAnthill = Building((1,2), ANTHILL, PLAYER_ONE)
sampTunnel = Building((3,2), TUNNEL, PLAYER_ONE)
playerOneTunnel = Building((8,8), TUNNEL, PLAYER_ONE)
sampFoodOne = Building((5,2), FOOD, PLAYER_ONE)
sampFoodTwo = Building((7,2), FOOD, PLAYER_ONE)
p1Inventory.ants.append(playerOneQueen)
p1Inventory.constrs.append(playerOneTunnel)
p1Inventory.constrs.append(sampFoodOne)
p1Inventory.constrs.append(sampFoodTwo)
p1Inventory.ants.append(sampAnt)
p1Inventory.ants.append(foodAnt)
p2Inventory.ants.append(enemyAnt)
p2Inventory.ants.append(enemyQueen)

#Fill board
board[0][0].ant = sampAnt
board[6][4].ant = enemyQueen
board[7][5].ant = playerOneQueen
board[1][2].constr = sampAnthill
board[8][8].constr = playerOneTunnel
board[3][2].constr = sampTunnel
board[5][2].constr = sampFoodOne
board[7][2].constr = sampFoodTwo
board[4][4].ant = foodAnt
board[3][4].ant = enemyAnt

#Initial state
state = GameState(board, [p1Inventory, p2Inventory, neutralInventory], MENU_PHASE, PLAYER_ONE)
player = AIPlayer(PLAYER_ONE)

#move an ant
move = Move(MOVE_ANT, [(0,0),(0,1), (1,1)], None)

#Evaluate state on move
tempState = player.checkState(state, move)

#Check if state is correct
if (tempState != None) and (getAntAt(tempState, (1,1)) != None):
    print "State constructed correctly."
else:
    print "State not constructed correctly after move."
    sys.exit(-1)

#Get score based on generate state and actual state of the game
moveScore = player.evaluateState(tempState, state)

#Check if evaluateState returns expected value 0.67
#moveScore converted to String because of Python rounding error
if str(moveScore) == "0.67":
    print "State evaluated correctly."
else:
    print "State not evaluated correctly. Expected value not returned"
    sys.exit(-1)

#Unit Test Success
print "Unit Test #1 Passed"