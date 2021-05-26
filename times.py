#!/usr/bin/python3.9

import re

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

# Validate number input
def getN(text):
    err = 0
    myIn = input(text)

    while (1):

        # Really wanted to use myIn.isdigit() here but I couldn't get it working
        if (re.search("^\d+$", myIn)):
            myIn = int(myIn)
            if (myIn > 0 and myIn < 13):
               break
        
        print("That's not a correct number.")
        err += 1

        # Too many errors, exit.
        if (err == 3):
            print("You are an idiot.")
            exit()

        myIn = input(text)

    
    return int(myIn)

name = getT("Welcome to Maths Quest!  What is your name? ")
table = getN(name + ", which times table would you like to practice? (1-12)  ")

print("Ok",  name + ": on a piece of paper, write down the", table, "times table from 1 to 12.  When you’re ready I’ll show you the answer so you can check your work.")

while (1):
    play = input("Are you ready? (Enter ‘y’ to start) ")
    if play.lower() == "y":
        break

l = []
l.extend(range(1, 13))

for i in l:
    print("%d x %d = %d" % (i, table, i * table))



while (1):
    ans = input("Did you get them all correct? (y/n) ")
    if ans.lower() == "y":
        print("Great job! Thank you for playing Maths Quest.")
        break
    elif ans.lower() == "n":
        print("Better luck next time!")
        break



