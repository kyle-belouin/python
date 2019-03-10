#Title: Rock, Paper, Scissors, Lizard, Spock!
#Purpose: It's a game!
#Original Author: Big Bang Theory
#Python Implementation: Kyle Belouin
#For: UNH-M COMP430
#Date: March 2019

import time
import random

#Defining the characters...since these are characters because I say so.
validChoices = ["rock", "scissors", "spock", "lizard", "paper"]
rockBeats = ["scissors", "lizard"]
scissorsBeats = ["lizard", "paper"]
spockBeats = ["scissors", "rock"]
lizardBeats = ["paper", "spock"]
paperBeats = ["scissors", "spock"]

player = "You"
opponent = "Computer"

playerLost = "You lost! The computer's move was: "
playerWon = "You won! The computer's move was: "

playAgain = ["", "no", "No"]

invalidInputMsg = "You have entered an invalid choice, please try again."

#Welcome player :) Read the rules
print("##############################################################################") #these serve no purpose other than a bit of art on screen.
print("Welcome to Rock, Paper, Scissors, Lizard, Spock!")
print("Here are the rules,")
print("Rock crushes scissors and crushes lizard, but is covered by paper and is vaporized by Spock.")
print("Scissors decapitates lizard and cuts paper, but is smashed by Spock.")
print("Spock smashes scissors and vaporizes rock, but is disproved by paper and is poisoned by Lizard.")
print("Lizard eats paper and poisons Spock, but is crushed by rock and decapitated by scissors.")
print("That's it!")
print("##############################################################################")
start = input("Ready to play? Press Enter when ready.")
type(start)

i = 50 #used below
computerWins = 0
playerWins = 0

while True:
	#Not that it matters, the computer will "move" first.
	print ("The computer is thinking... ")
	while i >= 0: #Some simulated thinking
		computerChoice = random.randint(0,4) #these will translate to array indicies
		i -= 1
		time.sleep(0.05) #using this to slow things down a bit, feels more human.
	computerMove = validChoices[computerChoice]
	print ("The computer has chosen.") 

	print("Player, it's your turn. Select your move.")
	print("Valid entries are rock, scissors, spock, lizard, or paper.")
	while True:
		playerMove = input("Enter your move: ") #asking user for input.
		type(playerMove)
		if (playerMove not in validChoices): #checking valid input
			print(invalidInputMsg)
		else:
			break #good choice, leave loop
	
	#Game logic	
	if (computerMove == playerMove):
		print("Draw!")
		
	if (computerMove == validChoices[0]):
		if(playerMove in rockBeats):
			print(playerLost + computerMove)
			computerWins += 1
		else:
			print(playerWon + computerMove)
			playerWins += 1
			
	if (computerMove == validChoices[1]):
		if(playerMove in scissorsBeats):
			print(playerLost + computerMove)
			computerWins += 1
		else:
			print(playerWon + computerMove)
			playerWins += 1
			
	if (computerMove == validChoices[2]):
		if(playerMove in spockBeats):
			print(playerLost + computerMove)
			computerWins += 1
		else:
			print(playerWon + computerMove)
			playerWins += 1
			
	if (computerMove == validChoices[3]):
		if(playerMove in lizardBeats):
			print(playerLost + computerMove)
			computerWins += 1
		else:
			print(playerWon + computerMove)
			playerWins += 1
			
	if (computerMove == validChoices[4]):
		if(playerMove in paperBeats):
			print(playerLost + computerMove)
			computerWins += 1
		else:
			print(playerWon + computerMove)
			playerWins += 1
			
	print("##############################################################################")
	computerWinsStr = str(computerWins)
	playerWinsStr = str(playerWins)
	print("The current scores are: ")
	print("Computer: " + computerWinsStr)
	print("Player: " + playerWinsStr)
	
	while True:
		endGameChoice = input("Do you want to play again? Press Enter or say no to quit. ")
		type(endGameChoice)
		if (endGameChoice not in playAgain):
			print(invalidInputMsg)
		else:
			break #good input, leave this loop
	if (endGameChoice == playAgain[0]):
		i = 50 #resetting this counter. The loop will now rerun.
	else:
		print("It's been a pleasure, goodbye!")
		break #leave game loop, program end.
