#!/usr/bin/python3.9
import re
import time

# Validate text input, make sure the name has a letter in it at least
def getT(text):
    err = 0
    myIn = input(text)

    while not (re.search("[a-zA-Z]", myIn)):
        print("Not a valid name.")

        err += 1

        # Too many errors, exit.
        if (err == 3):
            print("You are an idiot.")
            exit()
        
        myIn = input(text)
 
    return myIn


# Get choice and do some validation
def getC():
    print("Please choose:\n[R]ock\n[P]aper\n[S]cissors")
    choice = input(": ")
    while not (re.search("^[RPS]$", choice, re.IGNORECASE)):
        print("Only enter R, P or S.")
        choice = input(": ")

    return choice.upper()


def game():
    # Make it so we can modify the variables
    global score1
    global score2

    time.sleep(1)
    print(play2, "please close your eyes.\n")
    time.sleep(3)

    print(play1, "please choose what you want.")
    choice1 = getC()

    print("\n"*1000)
    print(play2, "it's your time to choose!")
    choice2 = getC()


    # Game logic
    print("\n\n")
    if (choice1 == choice2):
        print("It's a tie!")
    elif (choice1 == "R"):
        if (choice2 == "P"):
            print("[ %s ] WINS! Paper covers rock!" % play2)
            score2 += 1
        else:
            print("[ %s ] WINS! Rock smashes scissors!" % play1)
            score1 += 1
    elif (choice1 == "P"):
        if (choice2 == "S"):
            print("[ %s ] WINS! Scissors cuts paper!" % play2)
            score2 += 1
        else:
            print("[ %s ] WINS! Paper covers rock!" % play1)
            score1 += 1
    elif (choice1 == "S"):
        if (choice2 == "R"):
            print("[ %s ] WINS! Rock smashes scissors!" % play2)
            score2 += 1
        else:
            print("[ %s ] WINS! Scissors cuts paper" % play1);
            score1 += 1

    print("Scores: [%s has %s point(s)] and [%s - %s point(s)]\n" % (play1, score1, play2, score2)) 


score1 = 0
score2 = 0

print("Rock Paper Scissors V.1\n")

time.sleep(2)

play1 = getT("[ Player 1 ] What is your name? : ")
play2 = getT("[ Player 2 ] What is your name? : ")

print("\nHi " + play1 + " and " + play2 + "!\n")

while (1):
    game()

    play = input("Play again? ")
    if (re.search("^Y(ES)?$", play, re.IGNORECASE)):
        print("\n"*1000)
    else:
        exit()
