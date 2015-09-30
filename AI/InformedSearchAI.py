__author__ = 'Ryson Asuncion and Casey Sigelmann'

from Building import Building
from Inventory import Inventory
from Player import *
from Construction import Construction
from Ant import Ant
from GameState import GameState
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
        super(AIPlayer,self).__init__(inputPlayerId, "Sigelmann_Asuncion Informed Search")
        self.depthLimit = 2
        self.stepsToReachMap = []

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
        self.stepsToReachMap = []
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

        # initialize mapping of steps to reach
        if self.stepsToReachMap == []:
            for x in range(0, 10):
                verticleArray = []
                for y in range(0, 10):
                    # find the lowest steps to reach for food
                    stepsToReachFood = 999 # arbitrarily large number
                    for food in getConstrList(currentState, None, [FOOD]):
                        stepsToReachFood = min(stepsToReachFood, stepsToReach(currentState, (x, y), food.coords))

                    # find the lowest steps to reach for tunnel or anthill
                    stepsToReachTunnel = 999
                    for constr in getConstrList(currentState, self.playerId, [TUNNEL, ANTHILL]):
                        stepsToReachTunnel = min(stepsToReachTunnel, stepsToReach(currentState, (x, y), constr.coords))

                    # find the steps to reach for the opponent's anthill
                    opponentHill = getConstrList(currentState, (self.playerId+1)%2, [ANTHILL])[0]
                    stepsToReachOpponentHill = stepsToReach(currentState, (x,y), opponentHill.coords)
                    verticleArray.append((stepsToReachFood, stepsToReachTunnel, stepsToReachOpponentHill))

                self.stepsToReachMap.append(verticleArray)


        initNode = Node(None, currentState, None, 0.5)
        bestNode = self.bestMove(initNode, self.playerId, 0)
        return bestNode.move

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
    # processMove
    #
    # Parameters:
    #   currentState - The state of the current game
    #   move - The Move Action we want to analyze
    #
    # Return: A GameState object that represents how the game will look after
    #   the move is processed
    ##
    def processMove(self, currentState, move):

        clonedState = currentState.fastclone()

        # Find our inventory and enemies inventory
        clonedInventory = None
        enemyInventory = None
        if clonedState.inventories[PLAYER_ONE].player == self.playerId:
            clonedInventory = clonedState.inventories[PLAYER_ONE]
            enemyInventory = clonedState.inventories[PLAYER_TWO]
        else:
            clonedInventory = clonedState.inventories[PLAYER_TWO]
            enemyInventory = clonedState.inventories[PLAYER_ONE]

        # Check if move is a build move
        if move.moveType == BUILD:
            startCoord = move.coordList[0]
            if move.buildType == TUNNEL:
                #add new tunnel to inventory
                clonedInventory.foodCount -= CONSTR_STATS[move.buildType][BUILD_COST]
                tunnel = Building(startCoord, TUNNEL, self.playerId)
                clonedInventory.constrs.append(tunnel)
            else:     
                # Add a new ant to our inventory
                clonedInventory.foodCount -= UNIT_STATS[move.buildType][COST]
                antToBuild = Ant(startCoord, move.buildType, self.playerId)
                clonedInventory.ants.append(antToBuild)
        elif move.moveType == MOVE_ANT:
            startCoord = move.coordList[0]
            finalCoord = move.coordList[-1]
            # Update the coordinates of the ant to move
            for ant in clonedInventory.ants:
                if ant.coords == startCoord:
                    # update the ant's coords
                    ant.coords = finalCoord

                    #handle possible attacks, for now attack first that is eligible
                    for enemy in enemyInventory.ants:
                        if self.isValidAttack(ant, enemy.coords):
                            enemy.health -= UNIT_STATS[ant.type][ATTACK]
                            if enemy.health <= 0:
                                enemyInventory.ants.remove(enemy)
                            break
                        
                    # once we have moved the correct ant, we can stop checking ants
                    break
        elif move.moveType == END:
            foodList = getConstrList(currentState, None, [FOOD])
            for ant in clonedInventory.ants:
                # update worker's food carrying status if relevant
                if ant.type == WORKER:
                    finalCoords = ant.coords
                    if ant.carrying == False:
                        for food in foodList:
                            if finalCoords == food.coords:
                                ant.carrying = True
                    elif ant.carrying == True:
                        foodDeliveryConstrs = getConstrList(currentState, self.playerId, [ANTHILL, TUNNEL])
                        for constr in foodDeliveryConstrs:
                            if finalCoords == constr.coords:
                                ant.carrying = False
                                clonedInventory.foodCount += 1

        # set all ants to having not moved for the recursion
        for ant in clonedInventory.ants:
            ant.hasMoved = False

        # set whoseTurn to my turn for the recursion
        clonedState.whoseTurn = self.playerId

        return clonedState

    ##
    #isValidAttack
    #Description: Determines whether the attack with the given parameters is valid
    #   Attacking ant is assured to exist and belong to the player whose turn it is
    #
    #Parameters:
    #   attackingAnt - The Ant that is attacking (Ant)
    #   attackCoord - The coordinates of the Ant that is being attacked ((int,int))
    #
    #Returns: None if there is no attackCoord, true if valid attack, or false if invalid attack
    ##  
    def isValidAttack(self, attackingAnt, attackCoord):
        
        #we know we have an enemy ant
        rangeOfAttack = UNIT_STATS[attackingAnt.type][RANGE]
        diffX = abs(attackingAnt.coords[0] - attackCoord[0])
        diffY = abs(attackingAnt.coords[1] - attackCoord[1])
        
        #pythagoras would be proud
        if rangeOfAttack ** 2 >= diffX ** 2 + diffY ** 2:
            #return True if within range
            return True
        else:
            return False

    ##
    # evaluateState
    #
    # Description: Examines a GameState object and returns a double between 0 and 1 that indicates
    #   how good that stat is for the agent whose turn it is.
    #
    # Parameters:
    #   gameState - the GameState to be evaluated
    #
    # Returns: a Double indicating how good the state is
    def evaluateState(self, gameState):
        currentScore = 50

        # Find our inventory and enemies inventory
        if gameState.inventories[PLAYER_ONE].player == self.playerId:
            ourInventory = gameState.inventories[PLAYER_ONE]
            enemyInventory = gameState.inventories[PLAYER_TWO]
        else:
            ourInventory = gameState.inventories[PLAYER_TWO]
            enemyInventory = gameState.inventories[PLAYER_ONE]

        # Handle the score for workers
        foodDropOffs = getConstrList(gameState, self.playerId, [ANTHILL, TUNNEL])
        foodPickUps = getConstrList(gameState, None, [FOOD])
        for ant in ourInventory.ants:
            if ant.type == WORKER:
                if ant.carrying:
                    # want to get to tunnel
                    distanceTouple = self.stepsToReachMap[ant.coords[0]][ant.coords[1]]
                    distanceFromDest = distanceTouple[1]
                    currentScore += 25 - distanceFromDest
                else:
                    # want to get to food
                    distanceTouple = self.stepsToReachMap[ant.coords[0]][ant.coords[1]]
                    distanceFromDest = distanceTouple[0]
                    currentScore += 25 - distanceFromDest
            elif ant.type == QUEEN:
                for dropOff in foodDropOffs:
                    if ant.coords == dropOff.coords:
                        currentScore -= 10
                for pickUp in foodPickUps:
                    if ant.coords == pickUp.coords:
                        currentScore -= 10
                # get the queen as far from the enemey anthill as possible
                distanceTouple = self.stepsToReachMap[ant.coords[0]][ant.coords[1]]
                distanceFromEnemyHill = distanceTouple[2]
                currentScore += distanceFromEnemyHill
            elif ant.type == DRONE:
                # want to get to the opponent's tunnel
                distanceTouple = self.stepsToReachMap[ant.coords[0]][ant.coords[1]]
                distanceFromHill = distanceTouple[2]
                currentScore += 25 - distanceFromHill

        # Incentivize lowering the total health of the opponent's ants
        enemyHealth = 0
        queenHealth = 0
        for ant in enemyInventory.ants:
            if ant.type == QUEEN:
                queenHealth += 5 * ant.health
            else:
                enemyHealth += ant.health

        currentScore -= queenHealth
        currentScore -= enemyHealth

        # make sure we don't get too many workers
        numWorkers = len(getAntList(gameState, self.playerId, [WORKER]))
        if numWorkers > 2:
            currentScore -= 30 * numWorkers

        # make sure we don't get too many drones
        numDrones = len(getAntList(gameState, self.playerId, [DRONE]))
        if numDrones > 2:
            currentScore -= 30 * numDrones

        # make sure we don't build any other ants
        numOtherAnts = len(getAntList(gameState, self.playerId, [SOLDIER, R_SOLDIER]))
        if numOtherAnts > 0:
            currentScore -= 30 * numOtherAnts

        # incentivize gaining food
        currentScore += ourInventory.foodCount

        # incentivize capturing anthill
        enemyHill = getConstrList(gameState, enemyInventory.player, [ANTHILL])[0]
        currentScore -= 3 * enemyHill.captureHealth

        # make sure our return value is between 0 and 1
        currentScore = currentScore / 200.0
        if currentScore > 1.0:
            currentScore = 1.0
        elif currentScore < 0.0:
            currentScore = 0.0

        # check win conditions
        if ourInventory.foodCount > 10:
            currentScore = 1.0
        if enemyHill.captureHealth == 0:
            currentScore = 1.0
        isQueenDead = True
        for ant in enemyInventory.ants:
            if ant.type == QUEEN:
                isQueenDead = False
        if isQueenDead:
            currentScore = 1.0
        return currentScore


    def evaluateNodeList(self, nodeList):
        score = 0
        for node in nodeList:
            score += self.evaluateState(node.state)
        score /= len(nodeList)
        return score


    def bestMove(self, currentNode, playerId, currentDepth):
        # Base Case: at depth limit or winning move found
        if currentDepth > self.depthLimit or currentNode.evaluation == 1.0:
            return currentNode

        # Create a node for each state that can be reached from the current state
        legalMoves = listAllLegalMoves(currentNode.state)
        childList = []
        for move in legalMoves:
            childState = self.processMove(currentNode.state, move)
            childList.append(Node(move, childState, currentNode, self.evaluateState(childState)))

        # Create a dictionary to hold the nodes and their scores
        nodeDictionary = {}
        for node in childList:
            key = node.evaluation
            if not nodeDictionary.has_key(key):
                nodeDictionary[key] = []
            nodeDictionary[key].append(node)

        # Find the best score in the dictionary
        bestScore = max(nodeDictionary)

        # Recursive Step
        # Only look at nodes that have the max score and return the best option
        currentBestScore = -1.0
        currentBestNode = nodeDictionary[bestScore][0]
        for node in nodeDictionary[bestScore]:
            nextNode = self.bestMove(node, playerId, currentDepth + 1)
            if nextNode != node:
                node.evaluation = self.evaluateNodeList([nextNode, node])
            if node.evaluation > currentBestScore:
                currentBestScore = node.evaluation
                currentBestNode = node

        return currentBestNode


class Node(object):

    def __init__(self, initMove, potentialState, initParentNode, initEvaluation):
        self.move = initMove
        self.state = potentialState
        self.parentNode = initParentNode
        self.evaluation = initEvaluation