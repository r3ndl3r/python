#!/usr/bin/python3.9
import re
import random

# Difficulty settings
easy = "1-10"
hard = "1-100"

# Validate number input
def getN(text):
    err = 0
    myIn = input(text)

    while not (myIn.isdigit()):
        print("That's not a number.")
        err += 1

        # Too many errors, exit.
        if (err == 3):
            print("You are an idiot.")
            exit()

        myIn = input(text)

    
    return int(myIn)


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


print("Number Guessing V.1\n")
print("Hi " + getT("What is your name? : ") + "!\n")
print("What level game do you want to play?\n(H)ard\n(E)asy")

level = input(": ")
# Validation for game level input
while not (re.search("^[EH]$", level, re.IGNORECASE)):
    level = input(": ")


# Split the min and max numbers into an array and then get a random num
if (level.upper() == "E"):
    minMax = easy.split("-")
    secNum = random.randint(int(minMax[0]), int(minMax[1]))
    while (1):
        guess = getN("Enter a number between " + easy + " : ")
        if (guess == secNum):
            print("Yay you got it correct!")
            quit()
else:
    minMax = hard.split("-")
    secNum = random.randint(int(minMax[0]), int(minMax[1]))
    while (1):
        guess = getN("Enter a number between " + hard + " : ")
        if (guess == secNum):
            print("Yay you got it correct!")
            quit()


