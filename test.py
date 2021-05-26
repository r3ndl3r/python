#!/usr/bin/python3.9
import os.path
import re

#fn = input("Filename: ")

#if not (os.path.isfile(fn)):
#    print("File doesn't exists.")
#    quit()

#file = open(fn, "r")

#for line in file:
#    if (re.search("^\d{1,3}\.", line)):
#        os.system("ping " + line)

#file.close();

while (1):
    myIn = input("")
    if (re.search("^\d+$", myIn)):
        myIn = int(myIn)
        if (myIn > 0 and myIn < 13):
            print("Moo\n\n\n")