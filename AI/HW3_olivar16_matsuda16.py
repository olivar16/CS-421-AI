import random
import sys
import time
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
        super(AIPlayer,self).__init__(inputPlayerId, "Paul&Bryce's AI")
        self.DEPTH_LIMIT = 2

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
        theBest = self.searchTree(currentState, self.playerId, 0)
        return theBest

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
        
        for ant in ants:
            ant.hasMoved = False
        
        modifiedState.whoseTurn = self.playerId
        
        return modifiedState

    ##
    #evaluateNodes
    #Description: Evaluates a list of nodes
    #
    #Parameters:
    #nodeList - A list of Node objects
    #
    #Return: bestNode - Node with the best evaluation score
    ##
    def evaluateNodes(self, nodeList):
        maxEval = 0.0
        bestNode = None
        for node in nodeList:
            if node.stateEval > maxEval:
                bestNode = node
                maxEval = node.stateEval

        return bestNode
        
    ##
    # evaluateList
    # Description: evaluates overall list of nodes and returns a score.
    # In this case, it's the max eval value in the node list.
    #
    # Parameter: defList - list of node objects
    # Return: the biggest eval value in the list
    ##
    def evaluateList(self, defList):
        if not defList: return 0.0
        return self.evaluateNodes(defList).stateEval

    ##
    # tweakState
    # Description: alters state in the following two ways:
    #   i. sets all ants as having not moved (ant.hasMoved = False). 
    #      This allows us to look multiple steps in advance for a single ant.
    #   ii. set whoseTurn to always be your player's id
    #
    #
    # Parameters:
    # currenState - copy of the current game state (GameState)
    #
    # Return: copyState - the modified state with the aforementioned alterations
    ##
    def tweakState(self, currentState):
        copyState = currentState
        for ant in copyState.inventories[self.playerId].ants: 
            ant.hasMoved = False 
        copyState.whoseTurn = self.playerId
        return copyState

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
    def searchTree(self, currentState, PID, currentDepth):

        #Base case: currentDepth is at the depth limit
        if (currentDepth == self.DEPTH_LIMIT):
            return self.evaluate(currentState)
            

        #List of all Nodes containing states that can be reached from the current State
        nodeList = []

        #Get all legal moves in the current state
        moves = listAllLegalMoves(currentState)
       
       #For a more optimized search, get the first 10 moves
        precut = time.clock()
        moves = moves[:30]
       #Evaluate each move and store the 5 best moves with the highest evaluation scores
        topMoves = []
        for move in moves:
            reachState = self.checkState(currentState, move)
            reachState = self.tweakState(reachState)
            topMoves.append((move, self.evaluate(reachState)))
        #Get the top 5 moves based on evaluateState
        topMoves.sort(key=lambda tup:tup[1])
        topMoves = list(reversed(topMoves))        
        topMoves = topMoves[:5]

        for move in topMoves:
            reachState = self.checkState(currentState, move[0])
            reachState = self.tweakState(reachState)
            nodeEval = self.searchTree(reachState, PID, currentDepth + 1)
            node = self.Node(move[0], reachState, nodeEval)
            nodeList.append(node)
         # We're done recursing, return the overall best move
        if currentDepth == 0:
            bestNode = self.evaluateNodes(nodeList)
            return bestNode.move
        else:
            # We're still recursing up/down, return the score for this list of nodes.
            return self.evaluateList(nodeList)


    ##
    #evaluate
    #Description:  examines a GameState and returns a double
    #              between 0.0 and 1.0 that indicates how "good" that state is
    #
    #Parameters:
    #   gameState - the state to evaluate
    #
    #Returns: a double indicating the desirability of the state
    #         (from the current player's perspective)
    ##
    def evaluate(self, gameState):
        #get the player inventories
        myInv = gameState.inventories[self.playerId]

        opponentId = 0
        if self.playerId == 0:
            opponentId = 1
        opponentInv = gameState.inventories[opponentId]

        #get a list of tuple coordinates of my constructs
        buildings = getConstrList(gameState, self.playerId, (ANTHILL, TUNNEL))
        buildingCoords = []
        buildingCoords.append(buildings[0].coords)
        buildingCoords.append(buildings[1].coords)

        #get a list of tuple coordinates of all food on board
        food = getConstrList(gameState, None, (FOOD, ))
        foodCoords = []
        for foodObj in food:
            foodCoords.append(foodObj.coords)

        #base-case: if we win, return 1.
        if myInv.foodCount == 11 or opponentInv.getQueen() == None:
            return 1.0 #WIN

        #base-case: if the opponent wins, return 0.
        if opponentInv.foodCount == 11 or myInv.getQueen() == None:
            return 0.0 #LOSE

        #find and store coordinates of enemy queen
        enemyQueenCoords = opponentInv.getQueen().coords

        #compare food counts
        foodResult = (float(myInv.foodCount))/(float(FOOD_GOAL))

        #compare the ant counts
        allAnts = getAntList(gameState, pid=None)
        sumMyAnts = float(len(myInv.ants))
        sumOppAnts = float(len(opponentInv.ants))
        sumAllAnts = float(len(allAnts))
        antResult = (sumMyAnts - sumOppAnts)/(2*sumAllAnts) + 0.5

        #define a value for each ant type (sum of stats minus build cost)
        workerValue = 4.0
        droneValue = 6.0 
        soldierValue = 6.0 
        rangeValue = 5.0
        queenValue = 1.0

        #calculate stength of my army
        myAntSum = 0.0
        for myAnt in myInv.ants:
            if myAnt.type == WORKER:
                myAntSum = myAntSum + workerValue
            elif myAnt.type == DRONE:
                myAntSum = myAntSum + droneValue
            elif myAnt.type == SOLDIER:
                myAntSum = myAntSum + soldierValue
            elif myAnt.type == R_SOLDIER:
                myAntSum = myAntSum + rangeValue
            elif myAnt.type == QUEEN:
                myAntSum = myAntSum + queenValue
        #calculate strength of opponent's army
        oppAntSum = 0.0
        for oppAnt in opponentInv.ants:
            if oppAnt.type == WORKER:
                oppAntSum = oppAntSum + workerValue
            elif oppAnt.type == DRONE:
                oppAntSum = oppAntSum + droneValue
            elif oppAnt.type == SOLDIER:
                oppAntSum = oppAntSum + soldierValue
            elif oppAnt.type == R_SOLDIER:
                oppAntSum = oppAntSum + rangeValue
            elif oppAnt.type == QUEEN:
                oppAntSum = oppAntSum + queenValue
        armyStrength = (myAntSum - oppAntSum)/(2*(myAntSum + oppAntSum)) + 0.5

        #compare how many hit points enemy has vs total possible
        currentHealth = 0.0
        totalHealth = 0.0
        for ant in opponentInv.ants:
            currentHealth = currentHealth + ant.health
            totalHealth = totalHealth + UNIT_STATS[ant.type][HEALTH]
        hpPercent = 1.0 - currentHealth/totalHealth

        #evaulate an ant's distance from it's goal
        distanceSum = 0.0
        workers = 0.0
        carryingWorkers = 0.0
        for ant in myInv.ants:
            if ant.type == WORKER:
                workers = workers + 1.0 #keep count of how many workers we have
                #calculate distance ants are from food/building and keep a sum of the steps
                if ant.carrying:
                    carryingWorkers = carryingWorkers + 1.0
                    closestBuilding = self.findClosestCoord(gameState, ant.coords, buildingCoords)
                    buildingDistance = stepsToReach(gameState, ant.coords, closestBuilding)
                    distanceSum = distanceSum + buildingDistance/2.0
                else:
                    closestFood = self.findClosestCoord(gameState, ant.coords, foodCoords)
                    foodDistance = stepsToReach(gameState, ant.coords, closestFood)
                    distanceSum = distanceSum + foodDistance
            #all ants except worker and queen should pursue the enemy queen
            elif ant.type == DRONE or ant.type == R_SOLDIER or ant.type == SOLDIER:
                distanceSum = distanceSum + stepsToReach(gameState, ant.coords, enemyQueenCoords)

        #compare how many of our workers are carrying vs not carrying
        workerRatio = 0.0
        if workers > 0:
            distanceResult = 1.0 - distanceSum/(40*workers)
            if distanceResult < 0.0:
                distanceResult = 0.0
            workerRatio = carryingWorkers/workers
        else:
            distanceResult = 0.0

        #weight all considerations - higher multipliers = higher weight
        result = (foodResult*10.0 + antResult + armyStrength*8.0 + hpPercent + distanceResult + workerRatio/2.0)/22.5

        return result

    ##
    #findClosestCoord
    #Description: returns the closest in a list of coords from a specified
    #
    #Parameters:
    #   currentState - the current game state, as a GameState object
    #   src - the starting coordinate, as a tuple
    #   destList - a list of destination tuples
    #
    #Return: The closest coordinate from the list
    ##
    def findClosestCoord(self, currentState, src, destList):
        result = destList[0]
        lastDist = stepsToReach(currentState, src, result)

        #loop through to find the closest coordinates
        for coords in destList:
            currentDist = stepsToReach(currentState, src, coords)
            if currentDist < lastDist:
                result = coords
                lastDist = currentDist

        return result

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
        def __init__(self, move, reachState, stateEval):
            self.move = move
            self.reachState = reachState
            self.stateEval = stateEval
               
#UNIT TEST
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
p1Inventory.constrs.append(sampAnthill)
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

