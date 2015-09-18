import random
from Player import *
from Constants import *
from Construction import CONSTR_STATS
from Ant import UNIT_STATS, Ant
from Move import Move
from GameState import addCoords
from AIPlayerUtils import *

# Instance Variables
foodList = None

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
        super(AIPlayer,self).__init__(inputPlayerId, "Random")

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
        return moves[random.randint(0,len(moves) - 1)]

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

    def initializeFoodList(self, currentState):
        foodList = getConstrList(currentState, None, (FOOD))

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
        if foodList is None:
            self.initializeFoodList(currentState)
        clonedState = currentState.fastclone()

        # Find our inventory
        clonedInventory = clonedState.inventories[0]
        if clonedInventory.playerId != self.playerId:
            clonedInventory = clonedState.inventories[1]

        # Check if move is a build move
        if move.moveType == BUILD:
            # Add a new ant to our inventory
            antToBuild = Ant(move.coordList[0], move.buildType, self.playerId)
            clonedInventory.ants.append(antToBuild)
            antStats = UNIT_STATS[move.buildType]
            costToBuild = antStats[COST]
            clonedInventory.foodCount -= costToBuild
        elif move.moveType == MOVE_ANT:
            # Update the coordinates of the ant to move
            coordOfAnt = move.coordList[0]
            for ant in clonedInventory.ants:
                if ant.coords == coordOfAnt:
                    # update the ant's coords
                    finalCoords = move.coordList[-1]
                    ant.coords = finalCoords

                    # update worker's food carrying status if relevant
                    if ant.type == WORKER:
                        for food in foodList:
                            if finalCoords == food.coords:
                                ant.carrying = True
                        foodDeliveryConstrs = getConstrList(currentState, self.playerId, (ANTHILL, TUNNEL))
                        for constr in foodDeliveryConstrs:
                            if finalCoords == constr.coords:
                                ant.carrying = False
                                clonedInventory.foodCount += 1

                    break
