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
        print "NEW AIPLAYER INSTANTIATED"
        super(AIPlayer,self).__init__(inputPlayerId, "PaulGenetic")
        self.genes = []
        self.index = 0
        self.geneFitnessList = []
        self.generations = 0
        self.initializePopulation()
        self.firstMove = True
    
    
    
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


        #current gene
        currentGene = self.genes[self.index]

        print "The size of currentGene is " + str(len(currentGene))
        currCoords = []

        locations = []

        matrix = []

        #Ensure no duplicates
        #Anthill, tunnel and grass duplicate check
        for i in range(0, 13):
            if (currentGene[i],currentGene[i+13]) not in currCoords:
                currCoords.append((currentGene[i],currentGene[i+13]))
            else:
                print "curCoords is " + str(currCoords)
                print "DUPLICATE FOUND at " + str((currentGene[i],currentGene[i+13]))
                while (currentGene[i],currentGene[i+13]) in currCoords:
                    currentGene[i] = random.randint(0,9)
                    if i==11 or i==12:
                        currentGene[i+13] = random.randint(6,9)
                    else:
                        currentGene[i+13] = random.randint(0,3)
        currCoords.append((currentGene[i], currentGene[i+13]))

        # implemented by students to return their next move
        if currentState.phase == SETUP_PHASE_1:
             #  place ant hills

             numToPlace = 9
             for i in range(0, 11):
                 move = (currentGene[i],currentGene[i+13])
                 locations.append(move)
             anthill = locations[0]
             tunnel = locations[1]
             print "anthill placed at " + str(locations[0])
             print "tunnel placed at " + str(locations[1])
             return locations

        elif currentState.phase == SETUP_PHASE_2:   # stuff on foe's side

            for i in range(11, 13):
                while getConstrAt(currentState, (currentGene[i], currentGene[i+13])) is not None or (currentGene[11]==currentGene[12] and currentGene[24]== currentGene[25]):
                    currentGene[i] = random.randint(0,9)
                    currentGene[i+13] = random.randint(6,9)
                    # if currentGene[i] == 9 and currentGene[i+13] == 3:
                    #     currentGene[i] = 0
                    #     currentGene[i+13] = 0
                    # elif currentGene[i] == 9:
                    #     currentGene[i] = 0
                    #     currentGene[i+13] += 1
                    # else:
                    #     currentGene[i] +=1

             # set opponent id
            locations.append((currentGene[11], currentGene[24]))
            locations.append((currentGene[12], currentGene[25]))
            foodLocs.append(locations[0])
            foodLocs.append(locations[1])
            return locations

        else:
             return [(0, 0)]

        # #
    # initializePopulation
    # Description: Initializes the population of genes with random values and reset
    #              the fitness list to default values
    # Parameters:
    #    currentState - The state of the current game waiting for the player's move (GameState)
    #
    # Return: None
    # #
    def initializePopulation(self):
        #Start with N=100 genes
        numGenes = 5

        #Cells representing x and y coordinates of each object
        numCells = 26

        #Create N random genes
        for i in range(0,numGenes):

            gene = []
            for j in range(0, numCells):
                # set x values
                if j < 13:
                    gene.append(random.randrange(0, 9))
                # set y values
                else:
                    if j == 24 or j == 25:
                        gene.append(random.randrange(6, 9))
                    else:
                        gene.append(random.randrange(0, 3))
            self.genes.append(gene)

            #print "Gene " + str(i) + ":" + str(gene)

            #Initialize fitness of each gene to 0
            self.geneFitnessList.append(0)

    # #
    # evaluateFitness
    # Description: Evaluates the fitness of a gene based on distance of game objects from borders
    #
    # Parameters:
    #    gene - The list of coordinates to be evaluated
    #
    # Return: The evaluation score of the gene
    # #
    def evaluateFitness(self, gene):

        evalScore = 0

        xVals = gene[0:13]
        yVals = gene[13:26]

        #Evaluate distance between anthill and tunnel
        hillScore = abs(xVals[0] - xVals[1]) + abs(yVals[0] - yVals[1])

        #Evaluate food's closeness to the border
        foodScore = (9 - yVals[11]) + (9 - yVals[12])

        #Evaluate closeness of grass to the border
        grassScore=0

        for i in range(2, 11):
            grassScore+=yVals[i]

        evalScore = grassScore + hillScore + foodScore + grassScore
        return evalScore

    # #
    # mate
    # Description: Mates two parent genes and returns a child gene
    # Parameters:
    #    parentOne - First gene to mate
    #    parentTwo - Second gene to mate
    #
    # Return: the child gene that's a result of mating
    # #
    def mate(self, parentOne, parentTwo):

        child = []

        # Random pivot point to slice the gene for mating
        pivot = random.randrange(0, 26)
        print "pivot selected at " + str(pivot)
        childOne = parentOne[0:pivot] + parentTwo[pivot:26]
        childTwo = parentTwo[0:pivot] + parentOne[pivot:26]

        #Random mutation
        # randNum = random.randrange(0,26)
        # print "randNum is " + str(randNum)
        # if randNum==24 or randNum==25:
        #     childOne[randNum] = random.randrange(6,10)
        # elif randNum in range(13,24):
        #     childOne[randNum] = random.randrange(0,4)
        # else:
        #     print "randNum is within range 0 to 12"
        #     childOne[randNum] = random.randrange(0,11)
        #
        # randNumTwo = random.randrange(0,26)
        # if randNumTwo==24 or randNumTwo==25:
        #     childTwo[randNumTwo] = random.randrange(6,10)
        # elif randNum in range(13,24):
        #     childTwo[randNumTwo] = random.randrange(0,4)
        # else:
        #     childTwo[randNumTwo] = random.randrange(0,11)

        return [childOne, childTwo]

    # #
    # generateNextPopulation
    # Description: Creates a new population out of mated genes
    # Parameters:
    #
    #
    # Return: list containing the mated genes
    # #
    def generateNextPopulation(self):

        nextPopulation = []
        fitnessTuple = zip(self.geneFitnessList, self.genes)
        fitnessTuple.sort(reverse=True)
        print "fitnessTuple is " + str(fitnessTuple)
        sortedList=[]
        for element in fitnessTuple:
            #append the genes with the highest evaluation score
            sortedList.append(element[1])
        #sortedList = [x for y, x in fitnessTuple]
        print "sorted list for next population is " + str(sortedList)
        lenSortedList = len(sortedList)


        for i in range(0, lenSortedList/2):
            randNum1 = random.randrange(0, lenSortedList/2)
            randNum2 = random.randrange(0, lenSortedList/2)
            children = self.mate(sortedList[randNum1], sortedList[randNum2])
            nextPopulation.append(children[0])
            nextPopulation.append(children[1])

        #If it's odd, append the gene with the highest eval score
        if (lenSortedList%2 != 0):
            nextPopulation.append(sortedList[0])

        print "The size of next population is now " + str(len(nextPopulation))

        # parentList = sortedList[0:(lenSortedList / 2) + (lenSortedList % 2) + 1]
        # #parentList = sortedList[0, (lenSortedList / 2) + (lenSortedList % 2)]
        # print "parentList is " + str(parentList)
        # lenParentList = len(parentList)
        #
        #
        #
        # for i in range(0, lenParentList):
        #     randNum1 = random.randrange(0, lenParentList)
        #     randNum2 = random.randrange(0, lenParentList)
        #     while randNum1 == randNum2:
        #         randNum2 = random.randrange(0, lenParentList)
        #
        #     children = self.mate(parentList[randNum1], parentList[randNum2])
        #
        #     nextPopulation.append(children[0])
        #     nextPopulation.append(children[1])

        return nextPopulation

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
                    print "final move coord for ant is " + str(finalMoveCoords)
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
    #Description: Tells the player if they won or not
    #
    #Parameters:
    #   hasWon - True if the player won the game. False if they lost (Boolean)
    #
    def registerWin(self, hasWon):



         if hasWon:
             print "WON"

         self.geneFitnessList[self.index] += self.evaluateFitness(self.genes[self.index])

         self.firstMove = True

         print "Index: " + str(self.index)
         print "size of genes is " + str(len(self.genes))
         if self.index == len(self.genes)-1:
             self.generations+=1
             #if self.generations == 20:
             print "Generating next population"
             self.genes = self.generateNextPopulation()
             self.index = 0
             print "reached limit, index is now " + str(self.index)
         else:
             self.index+=1