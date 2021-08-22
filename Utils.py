import os
import time
from typing import Text
import FAN
import pickle

fans = []

path = os.path.join(os.getcwd(), "Settings.txt")
if os.path.exists(path) is True:
    settings = open(path, "r+")
else:
    settings = open(path, "w+")

def updateSettings():
    global settings

    # Check if Settings.txt exists if 
    # it does open in r+ mode else make one
    path = os.path.join(os.getcwd(), "Settings.txt")
    if os.path.exists(path) is True:
        settings = open(path, "r+")
    
    else:
        settings = open(path, "w+")
        settings.writelines(
            [
                "---SETTINGS---\n", 
                "\n", 
                "---ACCOUNTS---\n", 
                ""
            ]
        )


def removeAccount(buttonOut):
    global settings
    buttonOut, clear = buttonOut
    # Get user input
    name = buttonOut()

    # If there is input then
    if name != "":
        # make a new settings in read mode then read lines
        settings = open(os.path.join(os.getcwd(), "Settings.txt"), "r")
        lines = settings.readlines()
        
        if name.lower()+"\n" not in lines:
            print("[ERROR] Invalid input that fan does not exist")
            return
        
        # Remove the name from the file
        lines.remove(str(name.lower()+"\n"))

        try:
            # Delete the class file
            os.remove(os.path.join(os.getcwd(), name+".pkl"))

            # Get rid of the fan from the fans list
            for fan in fans:
                if fan.name.upper() == name.upper():
                    fans.remove(fan)
                    break
        except:
            pass
        
        # Re-write the file with new info
        open(os.path.join(os.getcwd(), "Settings.txt"), "w").writelines(lines)

        # Update settings
        updateSettings()

        # Clear input
        clear()
    
    # If user input not valid tell user
    else:
        print("[ERROR] Invalid input")


def loadFans():
    global fans, settings

    # Get the start position of the accounts
    start = 3
    lines = settings.readlines()
    for pos, line in enumerate(lines):
        if line.strip() == "---ACCOUNTS---":
            start = pos+1
    
    # Trim the list then re-establish all of the classes
    lines = lines[start:]
    for name in lines:
        # If account file does not exists but name 
        # exists in settings get rid of name in 
        # settings
        try:
            fan = pickle.load(open(os.path.join(os.getcwd(), name.replace("\n", "")+".pkl"), "rb"))
            fan.userToggleOn = False
            fan.userToggleOff = False
            fans.append(fan)
        
        except Exception as error:
            removeAccount((lambda : name.strip(), lambda : error))
    
    # Update settings
    updateSettings()


def saveFan(buttonOut):
    buttonOut, clear = buttonOut

    # Get the text
    text = buttonOut()

    # If the text is the valid format then
    if "\r" in text:
        try:

            # Split the text at \r then save that 
            # profile and add it to the list
            name, pin = text.split("\r")
            try:
                profile = FAN.Fan(int(pin), name.lower())
                profile.save(open(os.path.join(os.getcwd(), "Settings.txt"), "a+"))
                fans.append(profile)

                # Clear user input
                clear()
            except:
                print(f"[ERROR] Invalid input:\n{list(text)}")
        except:
            print("[ERROR] Invalid input\n[ERROR] \tError most likely caused by presing enter at the end of your input")
    
    # Else
    else:
        # Tell the user there is an error
        print(f"[ERROR] Invalid input:\n{list(text)}")
    
    updateSettings()

