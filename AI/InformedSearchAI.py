__author__ = 'Ryson Asuncion and Casey Sigelmann'

from Building import Building
from Inventory import Inventory
from Player import *
from Construction import Construction
from Ant import Ant
from GameState import GameState
from AIPlayerUtils import *
from Node import *


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

        # initialize mapping of steps to reach for workers
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

                    verticleArray.append((stepsToReachFood, stepsToReachTunnel))

                self.stepsToReachMap.append(verticleArray)

        #for x in range(0, 10):
            #for y in range (0, 10):
                #print "Coord(", x, ",", y, "): ", self.stepsToReachMap[x][y]

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
                    currentScore += 10 - distanceFromDest
                else:
                    # want to get to food
                    distanceTouple = self.stepsToReachMap[ant.coords[0]][ant.coords[1]]
                    distanceFromDest = distanceTouple[0]
                    currentScore += 10 - distanceFromDest
            elif ant.type == QUEEN:
                for dropOff in foodDropOffs:
                    if ant.coords == dropOff.coords:
                        currentScore -= 10
                for pickUp in foodPickUps:
                    if ant.coords == pickUp.coords:
                        currentScore -= 10

        # make sure we don't get too many workers
        if len(ourInventory.ants) > 3:
            currentScore -= 30

        # make sure our return value is between 0 and 1
        currentScore = currentScore / 100.0
        if currentScore > 1.0:
            currentScore = 1.0
        elif currentScore < 0.0:
            currentScore = 0.0

        # check win conditions
        if ourInventory.foodCount > 10:
            currentScore = 1.0
        if getConstrList(gameState, enemyInventory.player, [ANTHILL])[0] == 0:
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
        # Base Case: at depth limit
        if currentDepth > self.depthLimit:
            return currentNode

        # Create a node for each state that can be reached from the current state
        legalMoves = listAllLegalMoves(currentNode.state)
        childList = []
        for move in legalMoves:
            childState = self.processMove(currentNode.state, move)
            childList.append(Node(move, childState, currentNode, self.evaluateState(childState)))

        # Recursive Step
        currentBestScore = -1.0
        currentBestNode = childList[0]
        for node in childList:
            nextNode = self.bestMove(node, playerId, currentDepth + 1)
            if nextNode != node:
                node.evaluation = self.evaluateNodeList([nextNode, node])
            if node.evaluation > currentBestScore:
                currentBestScore = node.evaluation
                currentBestNode = node

        return currentBestNode






##################################
# Unit Test
##################################

# Create a GameState object
# antArray1 = [Ant((5,5), WORKER, PLAYER_ONE), Ant((1,1), QUEEN, PLAYER_ONE)]
# antArray2 = [Ant((8,8), QUEEN, PLAYER_TWO)]
#
# constrArray1 = [Construction((1,1), ANTHILL)]
# constrArray2 = [Construction((8,8), ANTHILL)]
# constrArray3 = [Construction((5,7), FOOD), Construction((4,4), FOOD)]
#
# inventory1 = Inventory(PLAYER_ONE, antArray1, constrArray1, 0)
# inventory2 = Inventory(PLAYER_TWO, antArray2, constrArray2, 0)
# inventory3 = Inventory(NEUTRAL, None, constrArray3, 0)
# inventories = [inventory1, inventory2, inventory3]
#
# stubState = GameState(None, inventories, PLAY_PHASE, PLAYER_ONE)
#
# # Create a Move object
# stubMove = Move(MOVE_ANT, [(5,5),(5,6),(5,7)], None)
#
# # Process the move
# testAIPlayer = AIPlayer(PLAYER_ONE)
# testProcessedState = testAIPlayer.processMove(stubState, stubMove)
#
# # Test that the ant moves correctly
# if testProcessedState.inventories[0].ants[0].coords != (5,7):
#     print "Resulting state after processMove was incorrect."
# else:
#     # Evaluate the state
#     if testAIPlayer.evaluateState(testProcessedState) != 0.5:
#         print "Evaluation of state was incorrect."
#     else:
#         print "Sigelmann_Underwood Search Unit Test #1 Passed"