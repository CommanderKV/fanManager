import pygame
import Utils
from datetime import time
from time import sleep

settings = Utils.settings


screen = 0
screens = []
selectedUser = None

class InputBox:
    def __init__(self, color, x, y, width, height):
        self.color = color
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = ""

    def draw(self, win, text="", outline=""):

        if outline:
            pygame.draw.rect(win, outline, (self.x-2,self.y-2,self.width+4,self.height+4),0)

        pygame.draw.rect(win, self.color, (self.x,self.y,self.width,self.height), 0)

        self.text = text

        if self.text == "":
            self.text = "Input"
        
        if self.text != "":
            font = pygame.font.SysFont("comicsans", 30)
            text = font.render(self.text, 1, (0,0,0))
            win.blit(text, (self.x + (self.width/2 - text.get_width()/2), self.y + (self.height/2 - text.get_height()/2)))

    def isOver(self, pos):
        # Pos is the mouse position or a tuple of (x,y) coordinates
        if pos[0] > self.x and pos[0] < self.x + self.width:
            if pos[1] > self.y and pos[1] < self.y + self.height:
                return True
            
        return False


class Screen:
    def __init__(self, buttons: list=[], text: list=[], other: list=[], inputBox: InputBox=None):
        self.win = pygame.Surface((500, 700))
        self.buttons = buttons
        self.text = text
        self.other = other
        self.inputBox = inputBox
        self.inputedText = ""

    def draw(self, WIN):
        self.win.fill((0, 0, 0))

        for other in self.other:
            other.draw(self.win)

        for button in self.buttons:
            button.draw(self.win)
        
        for text in self.text:
            text.draw(self.win)
        
        if self.inputBox != None:
            self.inputBox.draw(self.win, self.inputedText, outline=(255, 0, 0))
        
        WIN.blit(self.win, (0, 0))


class TextOnScreen:
    def __init__(self, color, x, y, text:str):
        self.color = color
        self.x = x
        self.y = y
        self.text = text
    
    def draw(self, win):
        font = pygame.font.SysFont("comicsans", 30)
        text = font.render(self.text, 1, self.color)
        win.blit(text, (self.x, self.y))


class Button():
    def __init__(self, color, x, y, width, height, text='', function=None, args=None):
        self.color = color
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = text
        self.function = function
        self.args = args

    def draw(self,  win, outline=None):
        #Call this method to draw the button on the screen
        if outline:
            pygame.draw.rect(win, outline, (self.x-2,self.y-2,self.width+4,self.height+4),0)
            
        pygame.draw.rect(win, self.color, (self.x,self.y,self.width,self.height),0)
        
        if self.text != '':
            font = pygame.font.SysFont('comicsans', 30)
            text = font.render(self.text, 1, (0,0,0))
            win.blit(text, (self.x + (self.width/2 - text.get_width()/2), self.y + (self.height/2 - text.get_height()/2)))

    def isOver(self, pos):
        #Pos is the mouse position or a tuple of (x,y) coordinates
        if pos[0] > self.x and pos[0] < self.x + self.width:
            if pos[1] > self.y and pos[1] < self.y + self.height:
                return True
            
        return False


class FanScreen:
    def __init__(self, name):
        self.win = pygame.Surface((500, 700))

        # Find the fan from the name
        for fan in Utils.fans:
            if fan.name.lower() == name.lower():
                self.fan = fan
                break
        else:
            print(f"[ERROR] Could not find fan with name '{name}'")

        leftPadding = 25
        topPadding = 25

        self.buttons = [
            Button((255, 255, 255), 330, 630, 150, 50, text="Save", function=self._saveInfo),
            Button((255, 255, 255), 20, 630, 150, 50, text="Back", function=changeScreen, args=3),
            Button(
                (255, 0, 0) if self.fan.autoTurnOn is False else (0, 255, 0), 
                leftPadding, 
                topPadding+190, 
                100, 
                50, 
                "Auto on", 
                function=self.autoTurnOnToggle
            ),
            Button(
                (255, 0, 0) if self.fan.autoTurnOff is False else (0, 255, 0), 
                leftPadding, 
                topPadding+270, 
                100, 
                50, 
                "Auto off", 
                function=self.autoTurnOffToggle
            )
        ]

        self.textBoxes = [
            TextOnScreen((255, 255, 255), leftPadding, topPadding, "Name"),
            TextOnScreen((255, 255, 255), leftPadding, topPadding+90, "Pin"),
            TextOnScreen((255, 255, 255), leftPadding+150, topPadding+170, "Auto on time"),
            TextOnScreen((255, 255, 255), leftPadding+150, topPadding+250, "Auto off time")
        ]

        self.inputBoxes = [
            InputBox((255, 255, 255), leftPadding, topPadding+20, 100, 50),
            InputBox((255, 255, 255), leftPadding, topPadding+110, 100, 50),
            InputBox((255, 255, 255), leftPadding+150, topPadding+190, 150, 50),
            InputBox((255, 255, 255), leftPadding+150, topPadding+270, 150, 50)
        ]
        
        self.inputtedTexts = [
            self.fan.name.title(),
            str(self.fan.pin),
            self.convertTime(self.fan.turnOnTime) if self.fan.turnOnTime != None else "",
            self.convertTime(self.fan.turnOffTime) if self.fan.turnOffTime != None else ""
        ]
        self.selectedInput = 0


    def convertTime(self, time) -> str:
        times = {
            24: 12,
            23: 11,
            22: 10,
            21: 9,
            20: 8,
            19: 7,
            18: 6,
            17: 5,
            16: 4,
            15: 3,
            14: 2,
            13: 1
        }

        # time: 21:45:00
        time = str(time)[:-3]
        
        # time: 21:45
        if int(time[0]) >= 1:
            if int(time[0]) == 2:
                time += " pm"

            elif int(time[1]) > 2:
                time += " pm"

            else:
                time += " am"

        elif time[0] == "0":
            time += " am"

        else:
            time += " am"

        # time: 08:00 am
        if time[0] == "0":
            time = time[1:]

        hour, minute = time.split(":")
        if int(hour) > 12:
            hour = times[int(hour)]
        
        time = str(hour)+":"+str(minute)
        
        # time: 8:00 am
        return time


    def autoTurnOnToggle(self, _=""):
        if self.fan.autoTurnOn is False:
            self.fan.autoTurnOn = True
            self.buttons[2].color = (0, 255, 0)
        else:
            self.fan.autoTurnOn = False
            self.buttons[2].color = (255, 0, 0)


    def autoTurnOffToggle(self, _=""):
        if self.fan.autoTurnOff is False:
            self.fan.autoTurnOff = True
            self.buttons[3].color = (0, 255, 0)
        else:
            self.fan.autoTurnOff = False
            self.buttons[3].color = (255, 0, 0)


    def _saveInfo(self, _=""):
        data = [
            self.fan.name.lower(),
            self.fan.pin,
            "" if self.fan.turnOnTime == None else self.convertTime(self.fan.turnOnTime),
            "" if self.fan.turnOffTime == None else self.convertTime(self.fan.turnOffTime)
        ]
        for pos, inputt in enumerate(self.inputtedTexts):
            if inputt != data[pos]:
                if pos == 0:
                    self.fan.name = inputt
                
                elif pos == 1:
                    try:
                        inputt = int(inputt)
                        self.fan.pin = inputt
                    except:
                        print("[ERROR] Invalid input for pin")

                elif pos == 2:
                    self.fan.turnOnTime = self.timeToTime(inputt)
                
                elif pos == 3:
                    self.fan.turnOffTime = self.timeToTime(inputt)
                
        
        self.fan.autoTurnOn = True if self.buttons[2].color == (0, 255, 0) else False
        self.fan.autoTurnOff = True if self.buttons[3].color == (0, 255, 0) else False

        self.fan.update()
        changeScreen(3)
        print("[INFO] Saved successfully")


    def timeToTime(self, timeIn) -> time:
        try:
            times = {
                1: 13,
                2: 14,
                3: 15,
                4: 16,
                5: 17,
                6: 18,
                7: 19,
                8: 20,
                9: 21,
                10: 22,
                11: 23,
                12: 24
            }
            # 9:45 | pm
            timeIn, prefix = timeIn.split(" ")
            # 9   |   45 
            hours, minutes = timeIn.split(":")

            if prefix.lower() == "pm":
                hours = times[int(hours)]
            
            #           21              | 45                  | pm
            return time(hour=int(hours), minute=int(minutes), microsecond=0)
        except:
            print("[ERROR] Invalid input\n[ERROR] Please write your time like this: '12:30 pm' not '12:30pm'")


    def draw(self, WIN):
        self.win.fill((0, 0, 0))

        for button in self.buttons:
            button.draw(self.win)
        
        for textBox in self.textBoxes:
            textBox.draw(self.win)
        
        for pos, inputBox in enumerate(self.inputBoxes):
            if self.selectedInput == pos:
                inputBox.draw(self.win, text=self.inputtedTexts[pos], outline=(255, 0, 0))
            else:
                inputBox.draw(self.win, text=self.inputtedTexts[pos])

        WIN.blit(self.win, (0, 0))



def draw(WIN, screenSelected):
    WIN.fill((0, 0, 0))

    screenSelected.draw(WIN)


def changeScreen(screenPos):
    global screen
    screen = screenPos


def clearScreenInputText():
    try:
        screens[screen].inputedText = ""
        return True
    except:
        return False


def getScreenInputText():
    return screens[screen].inputedText


def saveFan():
    fanNames = [fan.name.lower() for fan in Utils.fans]
    if getScreenInputText().split("\r")[0].lower() not in fanNames:
        Utils.saveFan((getScreenInputText, clearScreenInputText))
        screens.append(FanScreen(Utils.fans[-1].name))
        clearScreenInputText()
        updateFanPage()
    else:
        nameOut = getScreenInputText().split("\r")[0].title()
        print(f"[ERROR] Invalid input:\n[ERROR] \tFan with {nameOut} name already exists")


def removeFan():
    Utils.removeAccount((getScreenInputText, clearScreenInputText))
    updateFanPage()
    clearScreenInputText()


def updateFanPage():
    fanNames = [fan.name for fan in Utils.fans]
    buttons = [
        Button((255, 255, 255), 10, 640, 150, 50, text="Back", function=changeScreen, args=0),
        Button((135, 135, 135) if selectedUser == None else (255, 255, 255), 340, 640, 150, 50, text="Details", function=seeDetails),
        Button((135, 135, 135) if selectedUser == None else (255, 255, 255), 175, 640, 150, 50, text="Toggle", function=toggleFan)
    ]
    [buttons.append(Button((255, 0, 0) if fan.isFanOn() is False else (0, 255, 0), 175, 150+70*pos, 150, 50, fan.name.title(), function=selectUser, args=fan.name)) for pos, fan in enumerate(Utils.fans)]
    screens[3].buttons = buttons

    for screen in screens:
        if isinstance(screen, FanScreen) is True:
            if screen.fan.name not in fanNames:
                screens.remove(screen)

    if selectedUser != None:
        buttonNames = [button.text for button in screens[3].buttons]
        for pos, name in enumerate(buttonNames):
            if name.lower() == selectedUser.lower():
                button = screens[3].buttons[pos]
                button.color = (255, 0, 100) if button.color == (255, 0, 0) else (0, 255, 100)


def seeDetails():
    global selectedUser
    nameIn = selectedUser
    if nameIn != None:
        for pos, screen in enumerate(screens):
            if isinstance(screen, FanScreen) is True:
                if screen.fan.name == nameIn:
                    changeScreen(pos)
                    break


def selectUser(nameIn):
    global selectedUser
    #  none            kyler
    if selectedUser != nameIn:
        selectedUser = nameIn
    
    else:
        selectedUser = None
    screens[3].buttons[1].color = (255, 255, 255) if screens[3].buttons[1].color == (135, 135, 135) else (135, 135, 135)
    screens[3].buttons[2].color = (255, 255, 255) if screens[3].buttons[2].color == (135, 135, 135) else (135, 135, 135)


def toggleFan():
    global selectedUser
    nameIn = selectedUser
    if nameIn != None:
        for fan in Utils.fans:
            if fan.name == nameIn:
                if fan.isFanOn() is False:
                    fan.turnOn()
                else:
                    fan.turnOff()
                
                for button in screens[3].buttons:
                    if button.text.upper() == nameIn.upper():
                        button.color = (255, 0, 0) if fan.isFanOn() is False else (0, 255, 0)
                        break
                
                fan.update()
                break



def startDisplay():
    run = True
    Utils.loadFans()
    optionStart = 200
    size = (500, 700)
    pygame.font.init()
    clock = pygame.time.Clock()
    win = pygame.display.set_mode(size)

    # Main menu screen
    if True:
        buttons = [
            Button((255, 255, 255), 175, optionStart+50, 150, 50, text="Add fan", function=changeScreen, args=1),
            Button((255, 255, 255), 175, optionStart+120, 150, 50, text="Remove Fan", function=changeScreen, args=2),
            Button((255, 255, 255), 175, optionStart+190, 150, 50, text="Fans", function=changeScreen, args=3)
        ]
        
        screens.append(
            Screen(
                buttons=buttons, 
                text=[
                    TextOnScreen((255, 255, 255), 190, 50, "Main Menu")
                ]
            )
        )

    # Add fan
    if True:
        buttons = [
            Button((255, 255, 255), 330, 630, 150, 50, text="Save", function=saveFan),
            Button((255, 255, 255), 20, 630, 150, 50, text="Back", function=changeScreen, args=0)
        ]

        screens.append(
            Screen(
                buttons=buttons,
                text=[
                    TextOnScreen((255, 255, 255), 200, 50, "Add Fan"),
                    TextOnScreen((255, 255, 255), 90, 200, "Please enter the persons name then"),
                    TextOnScreen((255, 255, 255), 88, 220, "press enter then this will appear \n"),
                    TextOnScreen((255, 255, 255), 60, 240, "now put in the pin the fan is connected to.")
                ],
                inputBox=InputBox((255, 255, 255), 175, 300, 150, 50)
            )
        )
    
    # Remove fan
    if True:
        buttons = [
            Button((255, 255, 255), 330, 630, 150, 50, text="Save", function=removeFan),
            Button((255, 255, 255), 20, 630, 150, 50, text="Back", function=changeScreen, args=0)
        ]

        screens.append(
            Screen(
                buttons=buttons,
                text=[
                    TextOnScreen((255, 255, 255), 180, 50, "Remove Fan"),
                    TextOnScreen((255, 255, 255), 75, 250, "Please enter users name to delete it")
                ],
                inputBox=InputBox((255, 255, 255), 175, 300, 150, 50)
            )
        )
    
    # Fans
    if True:
        buttons = []
        textBoxes = [TextOnScreen((255, 255, 255), 220, 50, "Fans")]

        screens.append(
            Screen(
                buttons=buttons,
                text=textBoxes 
            )
        )

        updateFanPage()

    # Fan settings
    if True:
        for fan in Utils.fans:
            screens.append(FanScreen(fan.name))

    while run:
        clock.tick(10)

        # Run every tick items here

        for fan in Utils.fans:
            fan.check()

        updateFanPage()

        # End of run every tick items here

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            
            # If mouse button is pressed
            if event.type == pygame.MOUSEBUTTONDOWN:

                # Get mouse pos
                mousePos = pygame.mouse.get_pos()

                if isinstance(screens[screen], FanScreen) is False:
                    # Check if screen has buttons
                    if len(screens[screen].buttons) != 0:

                        # Go through each button on that screen
                        for button in screens[screen].buttons:

                            # If the mouse is over the button then call the function
                            if button.isOver(mousePos):
                                if button.function != None:
                                    if button.args != None:
                                        button.function(button.args)
                                    else:
                                        button.function()
                
                else:
                    # Go through each button on that screen
                    for button in screens[screen].buttons:

                        # If the mouse is over the button then call the function
                        if button.isOver(mousePos):
                            if button.function != None:
                                button.function(button.args)
                                break
                    else:
                        for pos, inputbox in enumerate(screens[screen].inputBoxes):
                            if inputbox.isOver(mousePos):
                                screens[screen].selectedInput = pos
                                break
                    

            # If a key is pressed check conditions
            if event.type == pygame.KEYDOWN:

                # Check for backspace
                if event.key == pygame.K_BACKSPACE:
                    if isinstance(screens[screen], FanScreen) is False:
                        screens[screen].inputedText = screens[screen].inputedText[:-1]
                    else:
                        screens[screen].inputtedTexts[screens[screen].selectedInput] = screens[screen].inputtedTexts[screens[screen].selectedInput][:-1]
                
                # Add text
                else:
                    if isinstance(screens[screen], FanScreen) is False:
                        screens[screen].inputedText += event.unicode
                    else:
                        screens[screen].inputtedTexts[screens[screen].selectedInput] += event.unicode
        
        # Draw the screen
        draw(win, screens[screen])

        # Update the screen
        pygame.display.update()
    
    pygame.quit()

if __name__ == "__main__":
    startDisplay()
