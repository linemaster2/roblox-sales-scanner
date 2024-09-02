import requests
import os
import json
from dotenv import dotenv_values

config = dotenv_values(".env")


class HashIds:
    @staticmethod
    def has_hashid(hash_id):
        with open("hashes.json") as file:
            all_hashes = json.load(file)
            return all_hashes.get(hash_id, False)

    def insert_hashid(hash_id):
        with open("hashes.json", "r") as file:
            all_hashes = json.load(file)

        all_hashes[hash_id] = True

        with open("hashes.json", "w") as file:
            json.dump(all_hashes, file, indent=4)

class Roblox:
    def __init__(self, cookie):
        self.cookie = cookie

    def get_id(self):
        cookies = {
            ".ROBLOSECURITY": self.cookie
        }

        r = requests.get("https://users.roblox.com/v1/users/authenticated", cookies=cookies)

        return r.json()["id"]

    def get_sales(self):
        user_id = self.get_id()

        params = {
            "cursor": "",
            "limit": 100,
            "transactionType": "Sale",
            "itemPricingType": "PaidAndLimited"
        }

        cookies = {
            ".ROBLOSECURITY": self.cookie
        }

        r = requests.get(f"https://economy.roblox.com/v2/users/{user_id}/transactions", params=params, cookies=cookies)

        return r.json()["data"]

    def check(self, user_id, gamepass_id): # user_id is the userid to check
        sales = self.get_sales()

        result = False

        for sale in sales:
            sale_user_id = sale["agent"]["id"]
            sale_product_id = sale["details"]["id"]
            hash_id = sale["idHash"]

            has_hash_id = HashIds.has_hashid(hash_id)

            if has_hash_id:
                continue # continue if the hashid already exists, that purchase has already been processed
            
            result = sale_user_id == user_id and sale_product_id == gamepass_id and not has_hash_id
            
            if (result):
                HashIds.insert_hashid(hash_id)
                break

        return result
    
            

rbx = Roblox(config["COOKIE"])

result = rbx.check(int(config["USER_ID_TO_CHECK"]), int(config["GAMEPASS_ID_TO_CHECK"])) # change these which ones to check
print(result)