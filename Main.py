# Welcome to the main coding that makes this cool project work :D. Please credit me if your plan on editing or sharing this project!

# all source code is on https://github.com/King-Clawthorne/Brick-Hill-Special-Sniper

# Made By Clawthorne (aka elevator) or Studios on brick-hill

import requests
from urllib.parse import unquote
from bs4 import BeautifulSoup
import os
import json
import math
from time import sleep
from time import time

# I was told I need to comment more in my scripts lol

timeSince = time()  # Just for the time since last check. gets the unix time.

session = (
    requests.session()
)  # this is the session for getting the latest items. It is not connected to the account

buyingSession = (
    requests.session()
)  # this session is only for when purchasing the special item. it is connected to the account

cookie1 = json.load(open("Config.json", "r"))

cookie = cookie1["Cookies"]

buyingSession.cookies.update(
    {"brick_hill_session": cookie}
)  # connecting to the account


def get_xsrf_token():  # brick hill doesnt let you send post requests without the xsrf token. So this initially gets it
    response = buyingSession.get(url="https://www.brick-hill.com/favorites/create")

    xsrf_cookie = response.cookies.get("XSRF-TOKEN")
    if xsrf_cookie:
        xsrf_token = unquote(xsrf_cookie)
        return xsrf_token
    else:
        return None


def strip_xsrf_token(
    xsrf_cookie,
):  # every time a post request is sent it sends a new xsrf cookie which i strip down to the token
    if xsrf_cookie:
        xsrf_token = unquote(xsrf_cookie)
        return xsrf_token
    else:
        return None


token = get_xsrf_token()  # xsrf token variable

# sets up the log
with open("log.txt", "w") as f:
    f.truncate(0)


def writeToLog(Text):
    with open("log.txt", "w") as f:
        f.write("\n\n")

        f.write(Text)


def GetNewItemData():  # uses the brick hill's api to get the latest brick hill official item and the data of the item
    def isSpecial(Data):
        special = Data["data"][0]["special_edition"]
        saleStatus = False
        if "stock_left" in Data["data"][0]:
            saleStatus = Data["data"][0]["stock_left"] or 0
        if special and saleStatus > 0:
            return {"Special": True, "Avalible": True}
        elif special and saleStatus == 0:
            return {"Special": True, "Avalible": False}
        else:
            return {"Special": False, "Avalible": True}

    Url = "https://api.brick-hill.com/v1/shop/list?sort=updated&limit=1"
    response = session.get(url=Url)

    if response.status_code == requests.codes.ok:
        jsonData = response.json()

        Special = isSpecial(jsonData)

        SpecialBool = Special["Special"]

        Avalible = Special["Avalible"]

        if SpecialBool:  # this returns the main information about the item
            return {"Special": True, "data": jsonData, "avalible": Avalible}
        else:
            return {"Special": False, "data": jsonData, "avalible": Avalible}
    else:
        return None


def GetPurchaseData(
    data,
):  # sets up data that will be needed for the payload of the post request
    DataInside = data["data"][0]

    creator = DataInside["creator"]["id"]

    price = 0

    Type = 2

    productID = DataInside["id"]

    if DataInside["bucks"] != None:
        price = DataInside["bucks"]
        Type = 2
    elif DataInside["bits"] != None:
        price = DataInside["bits"]
        Type = 1
    else:
        price = 0
        Type = 2

    returnTable = {
        "creator": creator,
        "price": price,
        "productid": productID,
        "purchasetype": Type,
    }

    return returnTable


def ReturnProductId(
    ItemId=355454,
):  # so apperently "ProductId" and "ItemId" are 2 seperate things. although annoying I found the product id inside the items html
    response = session.get(url=f"https://www.brick-hill.com/shop/{str(ItemId)}")

    soup = BeautifulSoup(response.content, "html.parser")

    div = soup.find(class_="col-10-12 push-1-12")

    product_id = div.find("item-page")[":product-id"]

    return int(product_id)


def Purchase(
    Plrid=1003, Price=0, productID=0, Purchasetype=0
):  # This is where the script sends a post request that buys the item after seeing that its avalible and a special item!
    global token
    PurchaseUrl = "https://www.brick-hill.com/shop/purchase"

    ProductID = ReturnProductId(productID)

    payload = {
        "product_id": ProductID,
        "purchase_type": Purchasetype,
        "expected_price": Price,
        "expected_seller": Plrid,
    }
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 OPR/98.0.0.0",
        "X-XSRF-TOKEN": token,
    }

    response = buyingSession.post(url=PurchaseUrl, data=payload, headers=headers)

    token = strip_xsrf_token(
        response.cookies.get("XSRF-TOKEN")
    )  # update the xsrf token

    if response.status_code == requests.codes.ok:
        writeToLog(
            f"Successfully attempted to buy item with the productid of {productID} for {Price} Bits/Credits!"
        )  # it will say this even if you didnt have enough credits or bits. im just too lazy to make it give seperate alerts for that stuff.
    else:
        writeToLog(
            f"Error buying {productID} for {Price} Bits/Credits with the status code {response.status_code}"
        )  # this will error if the return code is bad. probably the cookie.


def MainLoop():  # puts all the functions into action
    while True:
        ItemData = GetNewItemData()
        if ItemData != None:
            if (
                ItemData["Special"] and ItemData["avalible"]
            ):  # if the item is a special item and the item is avalible (meaning >0 stock) it will send a purchase request!
                purchaseData = GetPurchaseData(data=ItemData["data"])
                Purchase(
                    Plrid=purchaseData["creator"],
                    Price=purchaseData["price"],
                    productID=purchaseData["productid"],
                    Purchasetype=purchaseData["purchasetype"],
                )
            else:
                pass
            os.system("cls")  # clears the terminal to make it look fancy
            ItemName = ItemData["data"]["data"][0]["name"]
            global timeSince
            text = open("log.txt", "r").read()
            print(
                f"Latest Item: {ItemName}\nIs Special: {ItemData['Special']}\nIs Avalible: {ItemData['avalible']}\nTime Since Last Check: {math.floor((time() - timeSince)*100)/100}\n\n{text}"
            )
            timeSince = time()
        else:
            print(
                "\nError getting latest item! (Probably just being rate limited. Will try to restart in 5 seconds!)"
            )
            sleep(4.9)

        sleep(0.1)


MainLoop()
