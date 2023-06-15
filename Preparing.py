from os import system
from time import sleep
from json import dump


print("Downloading Requirements")

try:
    system("pip install -r requirements.txt")
except:
    print(
        "There was an error installing the requirements. please open cmd and install the requirements using 'pip install -r requirements.txt'. Thank you!"
    )

    sleep(5)


system("cls")


cookie = input(
    "Paste Cookie Using Instructions In README.MD (Using edit my cookie will not work!)\n\n"
)

with open("Config.json", "w") as f:
    f.truncate(0)

    tab = {"Cookies": cookie}

    dump(tab, f)


print("Cookie inputed! Thank you!")

input("Press Enter To Exit")
