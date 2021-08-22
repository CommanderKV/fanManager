import os
import time as timeos
import pickle
from datetime import date, time, datetime

class Fan:
    def __init__(self, pin, name):
        self.pin = int(pin)
        self.name = name

        self.state = False

        self.autoTurnOn = False
        self.autoTurnOff = True
        
        self.turnOnTime = None
        self.turnOffTime = time(hour=8, minute=0, second=0)

        self.userToggleOn = False
        self.userToggleOff = False


    def save(self, settings, new=True):
        try:
            if new is True:
                file = open(os.path.join(os.getcwd(), str(self.name)+".pkl"), "wb")
                pickle.dump(self, file)

                lines = settings.readlines()
                for pos, line in enumerate(lines):
                    if line == "---ACCOUNTS---":
                        lines.insert(pos+1, self.name.lower())
                        break
                
                settings.write(self.name.lower()+"\n")
            else:
                path = os.path.join(os.getcwd(), str(self.name)+".pkl")
                os.remove(path)
                while os.path.exists(path) is True:
                    os.remove(path)
                
                # print(self.__dict__)
                pickle.dump(self, open(path, "wb"))

            return True
        
        except:
            return False

    
    def update(self):
        path = os.path.join(os.getcwd(), str(self.name)+".pkl")
        os.remove(path)
        while os.path.exists(path) is True:
            os.remove(path)
        
        # print(self.__dict__)
        pickle.dump(self, open(path, "wb"))


    def check(self):
        if self.autoTurnOff is True or self.autoTurnOn is True:
            off = self.shutOffCheck()
            on = self.turnOnCheck()
            self.startCheck = timeos.time()

            if off == False and on == False:
                print("[ERROR] Error occurred!\n[ERROR] Attempted to turn on or off a fan\n[ERROR] automatically but it has failed\n")
                print(f"[ERROR] Variable states:\n[ERROR] \ton: {on}\n[ERROR] \toff: {off}\n")

        if self.startCheck+100000 < timeos.time():
            self.userToggleOff = False
            self.userToggleOn = False


    def shutOffCheck(self) -> bool:
        try:
            if self.state is True: # If fan is on
                if self.turnOffTime is not None:
                    if self.autoTurnOff is True: # If auto off is on
                        now = datetime.now() # Current time
                        currentTime = time( # Advanced current time
                            hour=now.hour, 
                            minute=now.minute, 
                            second=now.second
                        )

                        # If current time is greater than the turn 
                        # off time and user has not toggled on their fan then
                        if currentTime > self.turnOffTime and self.userToggleOn is False:
                            # Turn a pin to false or 0 here
                            print(f"[INFO] Automatically turned off {self.name}'s fan")
                            self.state = False
                            self.userToggleOff = False
                            self.update()
            return True
        
        except:
            return False


    def turnOnCheck(self) -> bool:
        try:
            if self.state is False: # If fan is off
                if self.autoTurnOn is True: # If auto on is on
                    if self.turnOnTime is not None: # If we have a turn on time
                        now = datetime.now() # Current time
                        currentTime = time( # Advanced current time
                            hour=now.hour, 
                            minute=now.minute, 
                            second=now.second
                        )

                        # If current time is greater than the turn on time and 
                        # user Toggle on is False
                        if currentTime > self.turnOnTime and self.userToggleOff is False:
                            # Turn a pin to True or 1
                            print(f"[INFO] Automatically turned on {self.name}'s fan")
                            self.state = True
                            self.userToggleOn = False
                            self.update
            return True
        
        except:
            return False


    def turnOn(self):
        # Turn a pin to True or 1
        # make sure that it did work 
        # with a try or something
        self.state = True
        self.userToggleOn = True
        return True # Or false depending on if it worked


    def turnOff(self):
        # Turn a pin to False or 0
        # make sure that it did work
        # with a try or something
        self.state = False
        self.userToggleOff = True
        return True # Or false depending on if it worked


    def isFanOn(self):
        return self.state

