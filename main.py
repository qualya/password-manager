from secrets import token_bytes
import time
import hashlib
import keyboard
import threading
import sys


arguments = sys.argv
if len(arguments) == 1:
    mode = "gui"
elif arguments[1] not in ["gui", "cmd"]:
    mode = "gui"
else:
    mode = arguments[1]


running = True
copying = True
#create window for gui mode
if mode == "gui":
    from tkinter import *
    import tkinter.font as font
    window = Tk()
    window.title('Password Manager')
    window.geometry("600x400")
    window.resizable(False, False)
    
    def end_program():
        global running
        running = False
        window.destroy()
        
    window.protocol("WM_DELETE_WINDOW", end_program)


#import words list
wordsList = list()
with open("words.txt", "r") as wordsFile: #the BIP39 words list
    for word in wordsFile:
        wordsList.append(word.replace("\n", ""))
    wordsFile.close()


def background():
    global clipboard
    global running
    global copying
    while running:
        try:
            if keyboard.is_pressed("ctrl+q") and copying:
                keyboard.write(clipboard)
        except:
            pass
        time.sleep(0.1)
            
b = threading.Thread(name='background', target=background)
b.start()


def hexToWords(hexKey, wordsList):
    private_key_num = int(hexKey, base=16) #converts the private key to base 10
    
    digits = [] #converts the base 10 private key into a list of base 2048
    while private_key_num:
        digits.append(int(private_key_num % 2048))
        private_key_num //= 2048
    digits = digits[::-1]
    
    mnemonic = list() #converts the digits into a mnemonic
    for number in digits:
        mnemonic.append(wordsList[number])
    
    return mnemonic


def wordsToHex(wordsKey, wordsList):
    digits = list() #converts the mnemonic into a list of digits in base 2048
    for word in wordsKey: #loops through the words in the mnemonic
        digits.append(wordsList.index(word)) #adds the position of the word of the mnemonic in the list of words
    digits.reverse()
    
    hexKey = 0
    for i in range(len(digits)): #loops through all of the base 2048 digits
        hexKey += digits[i]*2048**i #adds each of the digits in the base 2048 number multiplied by 2048 to the power of the digit's position to the previous number (the private key)
    hexKey = str(hex(hexKey))[2:] #converts the base 10 private key converted above into hexadecimal

    return hexKey



try:
    #starting question
    if mode == "gui":
        def makeChoice(ig):
            global choice
            choice = ig
            
        question = Label(window, text="Are you importing or generating a private key?", fg="black", font=("Courier", 15))
        question.place(x=20, y=25)
        importing = Button(window, font=("Courier", 20), text="Importing", height=5, width=16, command=lambda: makeChoice("1"))
        importing.place(x=20, y=80)
        generating = Button(window, font=("Courier", 20), text="Generating", height=5, width=16, command=lambda: makeChoice("2"))
        generating.place(x=310, y=80)
        
        choice = None
        while choice not in ("1", "2") and running:
            window.update()
            time.sleep(0.02)
        
        question.destroy()
        importing.destroy()
        generating.destroy()


    if mode == "cmd":
        print("Are you importing or generating a private key?")
        print("(1) importing")
        print("(2) generating")

        choice = None
        while choice not in ("1", "2"):
            choice = input("\nInput: ")
            if choice not in ("1", "2"):
                print("That is not a valid option, input '1' or '2'.")



    #importing private key
    if choice == "1":
        if mode == "gui":
            inputted = False
            def keySubmit(textKey):
                global key
                global inputted
                key = textKey
                inputted = True
                
            prompt = Label(window, text="Input your private key below.", fg="black", font=("Courier", 15))
            prompt.place(x=120, y=40)
            keyInput = Text(window, height=6, width=34, wrap=WORD)
            keyInput.place(x=120, y=100)
            submit = Button(window, font=("Courier", 10), text="Submit", height=5, width=9, command=lambda: keySubmit(keyInput.get("1.0", "end-1c")))
            submit.place(x=400, y=103)
            error = Label(window, text="This is an invalid key, please input a key in either hex form or words form.", fg="red", font=("Courier", 10), wraplength=400, justify="left")
            window.update()
            
        if mode == "cmd":
            print("\n\nInput your private key below.")
        
        properInput = False
        while properInput == False:
            if mode == "gui":
                while inputted == False and running:
                    window.update()
                    time.sleep(0.02)
                
            if mode == "cmd":
                key = input("\nInput: ")
                
            try:
                hexKey = key
                wordsKey = hexToWords(hexKey, wordsList)
                properInput = True
            except:
                try:
                    wordsKey = key.split(" ")
                    hexKey = wordsToHex(wordsKey, wordsList)
                    properInput = True
                except:
                    if mode == "gui":
                        error.place(x=120, y=210)
                        inputted = False
                        
                    if mode == "cmd":
                        print("This is an invalid key, please input a key in either hex form or words form.")
                    
        
        if mode == "gui":
            prompt.destroy()
            keyInput.destroy()
            submit.destroy()
            error.destroy()
            window.update()



    #generating private key
    if choice == "2":
        keyLength = "0"
        if mode == "gui":
            properInput = False
            def generateKey():
                global properInput
                global keyLength
                keyLength = keyLengthPrompt.get("1.0", "end-1c")
                if keyLength.isdigit() is False or keyLength == "0":
                    error.place(x=170, y=70)
                else:
                    properInput = True
                
            prompt = Label(window, text="Input the key size you want to generate below in bytes.", fg="black", font=("Courier", 13))
            prompt.place(x=20, y=20)
            
            keyLengthPrompt = Text(window, height=2, width=4)
            keyLengthPrompt.place(x=20, y=70)
            
            infoLabel = Label(window, text="Reference Sizes:\n8 bytes: 64 bits, 16 hexadecimal characters, or 6 words\n16 bytes: 128 bits, 32 hexadecimal characters or 12 words\n32 bytes: 256 bits, 64 hexadecimal characters or 24 words", fg="black", font=("Courier", 13), justify="left")
            infoLabel.place(x=15, y=120)
            
            generateButton = Button(window, font=("Courier", 10), text="Generate", height=2, width=10, command=generateKey)
            generateButton.place(x=70, y=66)
            
            error = Label(window, text="You must input an integer greater than 0.", fg="red", font=("Courier", 10))
            
            while properInput == False and running:
                window.update()
                time.sleep(0.02)
            
            prompt.destroy()
            keyLengthPrompt.destroy()
            infoLabel.destroy()
            generateButton.destroy()
            error.destroy()
            
            
        if mode == "cmd":
            print("\n\nInput the key size you want to generate below in bytes. For some references of sizes, input '?' below.")
            while keyLength.isdigit() is False or keyLength == "0":
                keyLength = input("\nInput: ")
                if keyLength == "?":
                    print("8 bytes: 64 bits, 16 hexadecimal characters, or 6 words")
                    print("16 bytes: 128 bits, 32 hexadecimal characters, or 12 words")
                    print("32 bytes: 256 bits, 64 hexadecimal characters, or 24 words")
                elif keyLength.isdigit() is False or keyLength == "0":
                    print("You must input an integer greater than 0.")
        
        
        hexKey = token_bytes(int(keyLength))
        hexKey = str(hexKey.hex()) #converts the key from bytes form to hex
        
        wordsKey = hexToWords(hexKey, wordsList)



    hexKey = hexKey.lstrip("0")
    if len(hexKey) == 0:
        hexKey = "0"

    if len(wordsKey) == 0:
        wordsKey = ["abandon"]
    while wordsKey[0] == "abandon" and len(wordsKey) > 1:
        wordsKey.pop(0)
    wordsKey = " ".join(wordsKey)



    if mode == "gui":
        def showFunction(show):
            keyLabel.configure(state="normal")
            if show == True:
                showKey.place_forget()
                keyLabel.insert(1.0, ("Hex Key:\n" + hexKey + "\n\nWords Key:\n" + wordsKey))
                hideKey.place(x=20, y=20)
            if show == False:
                hideKey.place_forget()
                keyLabel.delete(1.0, END)
                showKey.place(x=20, y=20)
            keyLabel.configure(state="disabled")
                
        showKey = Button(window, font=("Courier", 10), text="Show Key", height=5, width=10, command=lambda: showFunction(True))
        hideKey = Button(window, font=("Courier", 10), text="Hide Key", height=5, width=10, command=lambda: showFunction(False))
        showKey.place(x=20, y=20)
        
        keyLabel = Text(window, height=10, width=50, wrap=WORD)
        keyLabel.place(x=130, y=20)
        keyLabel.configure(state="disabled")
        
        notice = Label(window, text="NOTE: make sure to either write down or memorize one of the forms of the private key above.", fg="red", font=("Courier", 10), wraplength=400, justify="left")
        if choice == "2":
            notice.place(x=130, y=190)
        
        seedLabel = Label(window, text="Seed: ", fg="black", font=("Courier", 10))
        seedLabel.place(x=80, y=230)
        
        seedPrompt = Text(window, height=2, width=25)
        seedPrompt.place(x=130, y=230)
        
        truncateLabel = Label(window, text="Password Length: ", fg="black", font=("Courier", 10))
        truncateLabel.place(x=350, y=230)
        
        truncatePrompt = Text(window, height=2, width=5)
        truncatePrompt.place(x=490, y=230)
        
        passwordOutput = Text(window, height=5, width=50, wrap=WORD)
        passwordOutput.place(x=130, y=280)
        passwordOutput.configure(state="disabled")
        
        inputted = False
        def generate():
            global seed
            global truncate
            global inputted
            seed = seedPrompt.get("1.0", "end-1c")
            try:
                truncate = int(truncatePrompt.get("1.0", "end-1c"))
            except:
                truncate = 64
            inputted = True
        
        generateButton = Button(window, font=("Courier", 10), text="Generate", height=5, width=10, command=generate)
        generateButton.place(x=20, y=280)
        
        def getHelp():
            top = Toplevel(window)
            top.geometry("290x125")
            top.title("Seed Info")
            helpLabel = Label(top, text="Seeds can be usernames, website names,\ncombinations of those, or anything you want.\nFor simplicity, try to make your seeds memorable,\nand use a consistent pattern/format.\nExample seed format: 'username website_name'")
            helpLabel.place(x=10, y=5)
            okButton = Button(top, font=("Courier", 10), text="Okay", height=1, width=4, command=top.destroy)
            okButton.place(x=130, y=90)
        
        helpButton = Button(window, font=("Courier", 10), text="?", height=1, width=2, command=getHelp)
        helpButton.place(x=50, y=230)
        
        def toggleCtrlQ():
            global copying
            if copying == True:
                copying = False
                ctrlQOn.place_forget()
                ctrlQOff.place(x=20, y=120)
            elif copying == False:
                copying = True
                ctrlQOff.place_forget()
                ctrlQOn.place(x=20, y=120)
            
        ctrlQOn = Button(window, font=("Courier", 10), text="Ctrl+Q:\nOn", height=2, width=10, command=toggleCtrlQ)
        ctrlQOff = Button(window, font=("Courier", 10), text="Ctrl+Q:\nOff", height=2, width=10, command=toggleCtrlQ)
        ctrlQOn.place(x=20, y=120)
        

    if mode == "cmd":
        print("\n\nHex Key: " + hexKey)
        print("Words Key: " + wordsKey + "\n")
        if choice == "2":
            print("NOTE: make sure to either write down or memorize one of the forms of the private key above.")
        input("Press enter to continue.")
        print("\n\nInput any seed to generate a password for below. Seeds can be usernames, website names, combinations of those, or anything you want.")


    while running:
        if mode == "gui":
            while inputted == False and running:
                window.update()
                time.sleep(0.02)
            inputted = False
            
        if mode == "cmd":
            seed = input("\nSeed: ")
            try:
                truncate = int(input("Password Length: "))
            except:
                truncate = 64
        
        
        if seed != "":
            seed = seed + hexKey
            #hashing
            bytesString = seed.encode()
            encryptedHex = hashlib.sha256(bytesString).hexdigest()
            #truncation
            truncatedHex = encryptedHex[:truncate]
            #conversion to words
            encryptedWords = hexToWords(encryptedHex, wordsList)
            encryptedWords = " ".join(encryptedWords)
        else:
            truncatedHex = "None"
            encryptedWords = "None"
        
        
        if mode == "gui":
            passwordOutput.configure(state="normal")
            passwordOutput.delete(1.0, END)
            passwordOutput.insert(1.0, ("Hex Password: " + truncatedHex + "\n\nWords Password: " + encryptedWords))
            passwordOutput.configure(state="disabled")
            window.update()
            time.sleep(0.02)
        
        if mode == "cmd":
            print("Hex Password: " + truncatedHex)
            print("Words Password: " + encryptedWords)
        
        clipboard = truncatedHex

except:
    running = False
