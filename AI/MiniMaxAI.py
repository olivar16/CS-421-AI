__author__ = 'Paul Olivar and Casey Sigelmann'

##
# Parts of the eval function were from Bryce Matsuda
##

from Building import Building
from Inventory import Inventory
from Player import *
from Construction import Construction
from Ant import Ant
from GameState import GameState
from AIPlayerUtils import *
                
# establishing weights for the weighted linear equation
queenSafetyWeight = 0.3

# "max" values for determining how good a state is
maxDist = 18.0

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
        initNode = Node(None, currentState, None)
        bestNode = self.bestMove(initNode, self.playerId, 0)
        return bestNode.move
        
    ##
    # vectorDistance
    # Description: Given two cartesian coordinates, determines the 
    #   manhattan distance between them (assuming all moves cost 1)
    #
    # Parameters:
    #   self - The object pointer
    #   pos1 - The first position
    #   pos2 - The second position
    #
    # Return: The manhattan distance
    #
    def vectorDistance(self, pos1, pos2):
        return (abs(pos1[0] - pos2[0]) +
                    abs(pos1[1] - pos2[1]))
        
    ##
    # distClosestAnt
    # Description: Determines the distance between a cartesian coordinate
    #   and the coordinates of the enemy ant closest to it.
    #
    # Parameters:
    #   self - The object pointer
    #   currentState - The state to analyze
    #   initialCoords - The positition to check enemy ant distances from
    #
    # Return: The minimum distance between initialCoords and the closest
    #           enemy ant.
    #
    def distClosestAnt(self, currentState, initialCoords):
        # get a list of the enemy player's ants
        closestAntDist = 999
        for ant in currentState.inventories[(currentState.whoseTurn+1)%2].ants:
            tempAntDist = self.vectorDistance(ant.coords, initialCoords)
            if tempAntDist < closestAntDist:
                closestAntDist = tempAntDist
        return closestAntDist
        
        
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
    # hasWon
    # Description: Returns whether the given state results in a win for the given player
    #
    # Parameters:
    #   currentState - the state to be evaluated
    #   playerId - the current player
    #
    # Returns: True if the player won
    ##
    def hasWon(self, currentState, playerId):
        myInventory = currentState.inventories[playerId]
        enemyInventory = currentState.inventories[(playerId+1) % 2]
        if enemyInventory.getQueen() is None:
            return True
        if myInventory.foodCount >= 11:
            return True
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
    def evaluateState(self, currentState):
        # get a reference to the player's inventory
        playerInv = currentState.inventories[currentState.whoseTurn]
        # get a reference to the enemy player's inventory
        enemyInv = currentState.inventories[(currentState.whoseTurn+1) % 2]
        # get a reference to the enemy's queen
        enemyQueen = enemyInv.getQueen()
        
        # game over (lost) if player does not have a queen
        #               or if enemy player has 11 or more food
        if playerInv.getQueen() is None or enemyInv.foodCount >= 11:
            return 0.0
        # game over (win) if enemy player does not have a queen
        #              or if player has 11 or more food
        if enemyQueen is None or playerInv.foodCount >= 11:
            return 1.0
        
        # initial state value is neutral ( no player is winning or losing )
        valueOfState = 0.5        
            
        # hurting the enemy queen is a very good state to be in
        valueOfState += 0.025 * (UNIT_STATS[QUEEN][HEALTH] - enemyQueen.health)
        
        # keeps track of the number of ants the player has besides the queen
        numAttackAnts = 0
        enemyDistFromQueen = maxDist
        
        # loop through the player's ants and handle rewards or punishments
        # based on whether they are workers or attackers
        for ant in playerInv.ants:
            if ant.type == QUEEN:
                enemyDistFromQueen = self.distClosestAnt(currentState, ant.coords)
                queenSafety = enemyDistFromQueen / maxDist
                valueOfState += queenSafety * queenSafetyWeight
            else:
                numAttackAnts += 1
                # Punish the AI less and less as its ants approach the enemy's queen
                valueOfState -= 0.005 * self.vectorDistance(ant.coords, enemyQueen.coords)

        # punish AI for having no attack ants
        if numAttackAnts == 0:
            valueOfState -= 0.2
            
        # ensure that 0.0 is a loss and 1.0 is a win ONLY
        if valueOfState < 0.0:
            valueOfState = 0.001 + (valueOfState * 0.0001)
        if valueOfState > 1.0:
            valueOfState = 0.999
            
        # return the value of the currentState
        # Value if our turn, otherwise 1-value if opponents turn
        # Doing 1-value is the equivalent of looking at the min value
        # since it is the best move for the opponent, and therefore the worst move
        # for our AI
        if currentState.whoseTurn == self.playerId:
            return valueOfState
        return 1-valueOfState


    ##
    # evaluateNodeList
    # Description: Decides which node is best from a list of nodes
    #
    # Parameters:
    #   nodelist: the list of nodes to be evaluated
    #   playerId: the current player
    #
    # Returns: a node that is the best from the list
    ##
    def evaluateNodeList(self, nodeList, playerId):
        if len(nodeList) == 0:
            print "ERROR: evaluateNodeList called with empty list"

        nodeDictionary = {}
        for node in nodeList:
            key = node.evaluation
            if not nodeDictionary.has_key(key):
                nodeDictionary[key] = []
            nodeDictionary[key].append(node)

        if playerId == self.playerId:
            bestNodes = nodeDictionary[max(nodeDictionary.keys())]
        else:
            bestNodes = nodeDictionary[min(nodeDictionary.keys())]

        numTies = len(bestNodes)
        if numTies == 0:
            print "ERROR: No best node found"
        elif numTies == 1:
            bestNode = bestNodes[0]
        else:
            # Resolve ties by evaluating the state again. This should prioritize winning moves immediately.
            minimum = 1
            maximum = 0
            for node in bestNodes:
                evaluation = self.evaluateState(node.state)
                if playerId == self.playerId and evaluation > maximum:
                    maximum = evaluation
                    bestNode = node
                elif playerId != self.playerId and evaluation < minimum:
                    minimum = evaluation
                    bestNode = node

        return bestNode


    ##
    # bestMove
    # Description: Recursively gets the best child node for the given node
    #
    # Parameters:
    #   currentNode - the node to be expanded
    #   playerId - the current player
    #   currentDepth - how many recursions have occurred
    #
    # Returns: a node that is a child of the current node with the best evaluation
    ##
    def bestMove(self, currentNode, playerId, currentDepth):
        # Base Case: at depth limit or winning move found
        if currentDepth >= self.depthLimit:
            currentNode.evaluation = self.evaluateState(currentNode.state)
            return currentNode

        # Create a node for each state that can be reached from the current state
        legalMoves = listAllLegalMoves(currentNode.state)
        childList = []
        for move in legalMoves:
            childState = self.processMove(currentNode.state, move, playerId)
            childList.append(Node(move, childState, currentNode))

        # Recursive Step
        for node in childList:

            # Make sure winning moves are taken immediately
            if self.hasWon(node.state, playerId):
                currentNode.evaluation = node.evaluation
                return node

            # If the move type is end turn, then the next move will be for the opponent
            if node.move.moveType == END:
                nextNode = self.bestMove(node, (playerId+1) % 2, currentDepth + 1)
                if nextNode is None:
                    continue
            else:
                nextNode = self.bestMove(node, playerId, currentDepth + 1)
                if nextNode is None:
                    continue

            # Update parent node values for minimax
            if currentNode.state.whoseTurn == self.playerId:
                # Current node is a max node, so update its range accordingly
                if node.evaluation >= currentNode.min and node.evaluation <= currentNode.max:
                    currentNode.min = node.evaluation
            else:
                # Current node is a min node
                if node.evaluation >= currentNode.min and node.evaluation <= currentNode.max:
                    currentNode.max = node.evaluation

            # Check if the new bounds make it so we can be pruned
            parentNode = currentNode.parentNode
            if parentNode is None:
                continue
            if parentNode.state.whoseTurn == self.playerId:
                # parent was a max node
                if currentNode.max <= parentNode.min:
                    return None
            else:
                # parent was a min node
                if currentNode.min >= parentNode.max:
                    return None

        bestChildNode = self.evaluateNodeList(childList, playerId)
        currentNode.evaluation = bestChildNode.evaluation
        return bestChildNode


class Node(object):

    def __init__(self, initMove, potentialState, initParentNode):
        self.move = initMove
        self.state = potentialState
        self.parentNode = initParentNode
        self.evaluation = None
        self.min = 0.0
        self.max = 1.0
