__author__ = 'Paul Olivar and Casey Sigelmann'

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
        super(AIPlayer,self).__init__(inputPlayerId, "Sigelmann_Olivar MiniMax")
        self.depthLimit = 3
        self.PRUNED = 1234
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


        initNode = Node(None, currentState, None)
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
    def processMove(self, currentState, move, playerId):

        clonedState = currentState.fastclone()

        # Find our inventory and enemies inventory
        myInventory = None
        enemyInventory = None
        if clonedState.inventories[PLAYER_ONE].player == self.playerId:
            myInventory = clonedState.inventories[playerId]
            enemyInventory = clonedState.inventories[PLAYER_TWO]
        else:
            myInventory = clonedState.inventories[PLAYER_TWO]
            enemyInventory = clonedState.inventories[PLAYER_ONE]

        # Check if move is a build move
        if move.moveType == BUILD:
            startCoord = move.coordList[0]
            if move.buildType == TUNNEL:
                #add new tunnel to inventory
                myInventory.foodCount -= CONSTR_STATS[move.buildType][BUILD_COST]
                tunnel = Building(startCoord, TUNNEL, playerId)
                clonedState.inventories[playerId].constrs.append(tunnel)
            else:     
                # Add a new ant to our inventory
                myInventory.foodCount -= UNIT_STATS[move.buildType][COST]
                antToBuild = Ant(startCoord, move.buildType, playerId)
                clonedState.inventories[playerId].ants.append(antToBuild)
        elif move.moveType == MOVE_ANT:
            startCoord = move.coordList[0]
            finalCoord = move.coordList[-1]
            # Update the coordinates of the ant to move
            for ant in myInventory.ants:
                if ant.coords == startCoord:
                    # update the ant's coords
                    ant.coords = finalCoord
                    ant.hasMoved = True

                    #handle possible attacks, for now attack first that is eligible
                    for enemy in clonedState.inventories[playerId-1].ants:
                        if self.isValidAttack(ant, enemy.coords):
                            enemy.health -= UNIT_STATS[ant.type][ATTACK]
                            if enemy.health <= 0:
                                clonedState.inventories[playerId-1].ants.remove(enemy)
                            break
                        
                    # once we have moved the correct ant, we can stop checking ants
                    break
        elif move.moveType == END:
            foodList = getConstrList(currentState, None, [FOOD])
            for ant in clonedState.inventories[playerId].ants:
                # update worker's food carrying status if relevant
                if ant.type == WORKER:
                    finalCoords = ant.coords
                    if ant.carrying == False:
                        for food in foodList:
                            if finalCoords == food.coords:
                                ant.carrying = True
                    elif ant.carrying == True:
                        foodDeliveryConstrs = getConstrList(currentState, playerId, [ANTHILL, TUNNEL])
                        for constr in foodDeliveryConstrs:
                            if finalCoords == constr.coords:
                                ant.carrying = False
                                clonedState.inventories[playerId].foodCount += 1
            clonedState.whoseTurn = (clonedState.whoseTurn + 1) % 2

        # set all ants to having not moved for the recursion
        #for ant in clonedState.inventories[playerId].ants:
        #    ant.hasMoved = False

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
        # Find our inventory and enemies inventory
        if gameState.inventories[PLAYER_ONE].player == self.playerId:
            ourInventory = gameState.inventories[PLAYER_ONE]
            enemyInventory = gameState.inventories[PLAYER_TWO]
        else:
            ourInventory = gameState.inventories[PLAYER_TWO]
            enemyInventory = gameState.inventories[PLAYER_ONE]

        # Variables for determining the score with a linear equation
        workerScore = 0.0
        workerToggleFood = 0.0
        enemyQueenHealth = UNIT_STATS[QUEEN][HEALTH]
        otherEnemyHealth = 20.0
        droneScore = 0.0
        queenScore = 0.0
        numWorkersScore = 0.0
        numDronesScore = 0.0
        numOtherAntsScore = 0.0
        enemyHillHealth = 0.0
        foodCountScore = 0.0
        queenNotObstructingScore = 0.0
        totalEnemyMaxHealth = 0

        # Handle the score for workers
        foodDropOffs = getConstrList(gameState, self.playerId, [ANTHILL, TUNNEL])
        foodPickUps = getConstrList(gameState, None, [FOOD])
        for ant in ourInventory.ants:
            if ant.type == WORKER:
                if ant.carrying:
                    # want to get to tunnel
                    distanceTouple = self.stepsToReachMap[ant.coords[0]][ant.coords[1]]
                    # get the steps to reach tunnel from the touple
                    distanceFromDest = distanceTouple[1]
                    workerScore += 25.0 - distanceFromDest
                else:
                    # want to get to food
                    distanceTouple = self.stepsToReachMap[ant.coords[0]][ant.coords[1]]
                    # get the steps to reach food from the touple
                    distanceFromDest = distanceTouple[0]
                    workerScore += 25.0 - distanceFromDest
                if distanceFromDest == 0:
                    # We are either picking up food or dropping it off
                    workerToggleFood = 1.0
            elif ant.type == QUEEN:
                queenNotObstructing = True
                for dropOff in foodDropOffs:
                    if ant.coords == dropOff.coords:
                        queenNotObstructing = False
                for pickUp in foodPickUps:
                    if ant.coords == pickUp.coords:
                        queenNotObstructing = False
                if queenNotObstructing:
                    queenNotObstructingScore = 1.0
                # get the queen as far from the enemy anthill as possible
                distanceTouple = self.stepsToReachMap[ant.coords[0]][ant.coords[1]]
                distanceFromEnemyHill = distanceTouple[2]
                queenScore += distanceFromEnemyHill
            elif ant.type == DRONE:
                # want to get to the opponent's tunnel
                distanceTouple = self.stepsToReachMap[ant.coords[0]][ant.coords[1]]
                distanceFromHill = distanceTouple[2]
                droneScore += 25 - distanceFromHill

        # Incentivize lowering the total health of the opponent's ants
        for ant in enemyInventory.ants:
            if ant.type == QUEEN:
                enemyQueenHealth -= ant.health
            else:
                otherEnemyHealth -= ant.health

        # make sure we don't get too many workers
        numWorkers = len(getAntList(gameState, self.playerId, [WORKER]))
        if numWorkers > 2:
            numWorkersScore = 0.0
        else:
            numWorkersScore = 1.0

        # make sure we don't get too many drones
        numDrones = len(getAntList(gameState, self.playerId, [DRONE]))
        if numDrones > 1:
            numDronesScore = 0.0
        else:
            numDronesScore = 1.0

        # make sure we don't build any other ants
        numOtherAnts = len(getAntList(gameState, self.playerId, [SOLDIER, R_SOLDIER]))
        if numOtherAnts > 0:
            numOtherAntsScore = 0.0
        else:
            numOtherAntsScore = 1.0

        # incentivize gaining food
        foodCountScore = ourInventory.foodCount

        # incentivize capturing anthill
        enemyHill = getConstrList(gameState, enemyInventory.player, [ANTHILL])[0]
        enemyHillHealth = CONSTR_STATS[ANTHILL][CAP_HEALTH] - enemyHill.captureHealth

        # Normalize scores for linear equation
        workerScore /= 50.0
        if workerScore > 1.0:
            workerScore = 1.0
        queenNotObstructingScore /= 1.0
        queenScore /= 30.0
        droneScore /= 25.0
        enemyQueenHealth /= 4.0
        otherEnemyHealth /= 20.0
        numWorkersScore /= 1.0
        numDronesScore /= 1.0
        numOtherAntsScore /= 1.0
        foodCountScore /= 11.0
        workerToggleFood /= 1.0
        enemyHillHealth /= CONSTR_STATS[ANTHILL][CAP_HEALTH]

        evaluation = 0.15 * workerScore + \
                     0.25 * workerToggleFood + \
                     0.25 * foodCountScore + \
                     0.1 * queenScore + \
                     0.25 * numWorkersScore
                     # 0.01 * queenNotObstructingScore + \

                     # 0.01 * droneScore + \
                     # 0.25 * enemyQueenHealth + \
                     # 0.05 * otherEnemyHealth + \

                     # 0.15 * numDronesScore + \
                     # 0.05 * numOtherAntsScore + \


                     # 0.01 * enemyHillHealth + \

        # make sure our return value is between 0 and 1
        if evaluation > 1.0:
            evaluation = 1.0
        elif evaluation < 0.0:
            evaluation = 0.0

        # check win conditions
        if ourInventory.foodCount > 10:
            evaluation = 1.0
        if enemyHill.captureHealth == 0:
            evaluation = 1.0
        isQueenDead = True
        for ant in enemyInventory.ants:
            if ant.type == QUEEN and ant.health > 0:
                isQueenDead = False
        if isQueenDead:
            evaluation = 1.0

        return evaluation


    def evaluateNodeList(self, nodeList, playerId):
        min = 1
        max = 0
        if len(nodeList) == 0:
            print "ERROR: evaluateNodeList called with empty list"
        bestNode = nodeList[0]
        if playerId == self.playerId:
            for node in nodeList:
                if node.evaluation > max:
                    max = node.evaluation
                    bestNode = node
        else:
            for node in nodeList:
                if node.evaluation < min:
                    min = node.evaluation
                    bestNode = node
        return bestNode


    def bestMove(self, currentNode, playerId, currentDepth):
        # Base Case: at depth limit or winning move found
        if currentDepth >= self.depthLimit:
            currentNode.evaluation = self.evaluateState(currentNode.state)
            parentNode = currentNode.parentNode
            # Update parent node values for minimax
            if parentNode.state.whoseTurn == self.playerId:
                # Parent was a max node, so update its range accordingly
                if currentNode.evaluation >= parentNode.min and currentNode.evaluation <= parentNode.max:
                    parentNode.min = currentNode.evaluation
            else:
                # Parent was a min node
                if currentNode.evaluation >= parentNode.min and currentNode.evaluation <= parentNode.max:
                    parentNode.max = currentNode.evaluation

            return currentNode

        # Create a node for each state that can be reached from the current state
        legalMoves = listAllLegalMoves(currentNode.state)
        childList = []
        for move in legalMoves:
            childState = self.processMove(currentNode.state, move, playerId)
            childList.append(Node(move, childState, currentNode))

        # Create a dictionary to hold the nodes and their scores
        # nodeDictionary = {}
        # for node in childList:
        #     key = node.evaluation
        #     if not nodeDictionary.has_key(key):
        #         nodeDictionary[key] = []
        #     nodeDictionary[key].append(node)

        # Find the best score in the dictionary
        # bestScore = max(nodeDictionary)

        # Recursive Step
        # Only look at nodes that have the max score and return the best option
        # for node in nodeDictionary[bestScore]:
        for node in childList:
            # if currentDepth == 0 and node.move.moveType == END:
            #     # print "END TURN"
            if node.move.moveType == END:
                nextNode = self.bestMove(node, (playerId+1) % 2, currentDepth + 1)
                if nextNode == self.PRUNED:
                    print "Node pruned"
                    continue
            else:
                nextNode = self.bestMove(node, playerId, currentDepth + 1)
                if nextNode == self.PRUNED:
                    print "Node pruned"
                    continue
            if nextNode != node:
                node.evaluation = nextNode.evaluation
                # Update parent node values for minimax
                if currentNode.state.whoseTurn == self.playerId:
                    # Parent was a max node, so update its range accordingly
                    if node.evaluation >= currentNode.min and node.evaluation <= currentNode.max:
                        currentNode.min = node.evaluation
                else:
                    # Parent was a min node
                    if node.evaluation >= currentNode.min and node.evaluation <= currentNode.max:
                        currentNode.max = node.evaluation
            grandparentNode = currentNode.parentNode
            if grandparentNode is None:
                continue
            if grandparentNode.state.whoseTurn == self.playerId:
                if currentNode.max <= grandparentNode.min:
                    # prune
                    return self.PRUNED
            else:
                if currentNode.min >= grandparentNode.max:
                    return self.PRUNED

        # return self.evaluateNodeList(nodeDictionary[bestScore], playerId)
        return self.evaluateNodeList(childList, playerId)


class Node(object):

    def __init__(self, initMove, potentialState, initParentNode):
        self.move = initMove
        self.state = potentialState
        self.parentNode = initParentNode
        self.evaluation = 0.5
        self.min = 0.0
        self.max = 1.0
