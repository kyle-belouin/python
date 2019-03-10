#Title: War
#Purpose: It's a game!
#Python-Implementation: Kyle Belouin
#For: UNH-M COMP430

import random
import time

possibleCards = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13]
theDeck = []
deckIndex = 0
playerCards = []
playerIndex = 0
computerCards = []
computerIndex = 0
totalCards = 52
endGameChoice = ""

playerWin = "You have won the round!"
computerWin = "You have lost the round!"

playAgain = ["", "quit"]

print("##############################################################################")
print("Welcome to War!")
print("In this game, the goal is to empty your hand of cards.")
print("The game starts with each player getting dealt half the deck of cards.")
print("Each round, each player plays a card. The card with the higher value is the winner of the round.")
print("Their card goes to the opponent and is added to their deck.")
print("If each player places the same value card, this means war!")
print("Each player places four cards. The value of the last card determines who wins the war.")
print("Whoever has the higher value wins and gives the cards played in the war to the opponent to add to their stack.")
print("##############################################################################")

start = input("Ready to play? Press Enter when ready.")
type(start)

while True: #The game at large
    print("Shuffling the cards")
    while totalCards > 0: #generating a random deck of cards, or you could call this shuffling :)
        theDeck.append (random.randint(1,13))
        totalCards -= 1
        time.sleep(0.05) #This is pointless, only to give the game a more human feel.
    
    print("Distributing cards to the players")
    while deckIndex <= 51: #distributing cards to the players
        playerCards.append (theDeck[deckIndex])
        deckIndex += 1
        computerCards.append (theDeck[deckIndex])
        deckIndex += 1
        time.sleep(0.05)
        
    while True: #The game logic lives in this
        numPlayerCards = len(playerCards)
        numComputerCards = len(computerCards)
        stringPlayerCards = str(numPlayerCards) #these are integers that need to be strings
        stringComputerCards = str(numComputerCards)
        
        playerCard = str(playerCards[playerIndex])
        computerCard = str(computerCards[computerIndex])
        print("The computer has placed " + (computerCard))
        print("You have placed " + (playerCard))
        computerIndexStr = str(computerIndex) #debug
        playerIndexStr = str(playerIndex)
        #print("DEBUG, COMPUTER INDEX " + computerIndexStr)
        #print("DEBUG, PLAYER INDEX " + playerIndexStr)
        time.sleep(1) #giving the human player some time to process this
        
        if (playerCards[playerIndex]) == (computerCards[computerIndex]): #war
            print("This means WAR!!!")
            i = 0
            playersWarCards = [] #cards to be used for the war.
            computersWarCards = []
            currentPlayerIndex = playerIndex #used later
            currentComputerIndex = computerIndex #used later
            while i <= 3: #select these from the first four cards already lined up.
                playersWarCards.append (playerCards[playerIndex])
                playerIndex += 1
                computersWarCards.append (computerCards[computerIndex])
                computerIndex += 1
                i += 1
                time.sleep(0.1)
                
            playerPlaced = str(playersWarCards)
            computerPlaced = str(computersWarCards)
            
            print("You placed" + playerPlaced)
            print("The computer placed" + computerPlaced)
            time.sleep(1) #time for the human to process
        
            if (playersWarCards[3]) > (computersWarCards[3]): #the final cards placed in the war
                print("You have won the war!")
                computerCards.append (playersWarCards) #add our war cards to their deck
                computerIndex - 4 #compensating for the computer getting 4 new cards
                i = 0
                playerCardStr = str(playerCards) #debug
                while i <= 3: #this serves to remove the exact four cards from our deck that the opponent is receiving. 
                    #playerCards.remove (playerCards[currentPlayerIndex]) #debug
                    del (playerCards[currentPlayerIndex])
                    print(playerCardStr) #debug
                    currentPlayerIndex += 1
                    i += 1
                time.sleep(2) #time for the human to process.    
                print("Player has " + stringPlayerCards) #debug
                print("Computer has " + stringComputerCards) #debug
            else:
                print("You have lost the war!")
                playerCards.append (computersWarCards) #add their war cards to our deck
                playerIndex - 4 #compensating for the player getting 4 new cards
                i = 0
                compCardStr = str(computerCards)
                while i <= 3: #this serves to remove the exact four cards from our deck that the opponent is receiving. 
                    #computerCards.remove (computerCards[currentComputerIndex]) #debug
                    del computerCards[currentComputerIndex]
                    print(compCardStr) #debug
                    currentComputerIndex += 1
                    i += 1
                time.sleep(2) #time for the human to process
                print("Player has " + stringPlayerCards) #debug
                print("Computer has " + stringComputerCards) #debug
        
        elif (playerCards[playerIndex]) > (computerCards[playerIndex]):
            computerCards.append (playerCards[playerIndex])
            playerCards.remove (playerCards[playerIndex]) #this and above work to transfer the cards to the opponent.
            playerIndex += 1
            #note, computerIndex is not updated so we can accomodate for their +1 of a card.
            print(playerWin)
            print("Player has " + stringPlayerCards) #debug
            print("Computer has " + stringComputerCards) #debug
        else:
            playerCards.append (computerCards[computerIndex])
            computerCards.remove (computerCards[computerIndex]) #this and above work to transfer the cards to the opponent.
            #playerIndex is not updated so we can accomodate for their +1 of a card.
            computerIndex += 1
            print(computerWin)
            print("Player has " + stringPlayerCards) #debug
            print("Computer has " + stringComputerCards) #debug
        
        if (numPlayerCards == 0):
            print("Player, you have won the game!")
            break #drop from this loop into end game conditions.
        if (numComputerCards == 0):
            print("Player, you have lost the game!")
            break
        
    if (numPlayerCards == "0") | (numComputerCards == "0"): #game is over. Play again?
        while True:
            endGameChoice = input("Do you want to play again? Press Enter or say quit. ")
            type(endGameChoice)
            if (endGameChoice not in playAgain): #checking valid input
                print(invalidInputMsg)
            else:
                break #good input, leave this loop
            
    if (endGameChoice == playAgain[0]): #resetting game vars
        theDeck = []
        deckIndex = 0
        playerCards = []
        numPlayerCards = len(playerCards)
        playerIndex = 0
        computerCards = []
        numComputerCards = len(computerCards)
        computerIndex = 0
        totalCards = 52
    else:
        print("It's been a pleasure, goodbye!")
        break #leave game loop, program end.
