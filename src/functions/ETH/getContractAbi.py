import os
import requests
from dotenv import load_dotenv
import json

load_dotenv()

ETHERSCAN_API_KEY = os.getenv("ETHERSCAN_API_KEY")
ETHERSCAN_API_URL = "https://api.etherscan.io/api"

def get_contract_abi(contract_address: str):
    print(f"[ETH] Fetching ABI for contract: {contract_address}")

    try:
        response = requests.get(ETHERSCAN_API_URL, params={
            "module": "contract",
            "action": "getabi",
            "address": contract_address,
            "apikey": ETHERSCAN_API_KEY,
        }, timeout=30)

        response.raise_for_status()
        data = response.json()
        status = data.get("status")
        message = data.get("message")
        result = data.get("result")

        if status != "1":
            print(f"[ETH] ABI fetch failed: {message}")
            return None

        abi = json.loads(result)
        print(f"[ETH] ABI successfully fetched for {contract_address}")
        return abi

    except Exception as err:
        print(f"[ETH] Error fetching ABI for {contract_address}: {err}")
        return None

def is_contract(address: str) -> bool:
    try:
        response = requests.get(ETHERSCAN_API_URL, params={
            "module": "contract",
            "action": "getabi",
            "address": address,
            "apikey": ETHERSCAN_API_KEY,
        }, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data.get("status") == "1"
    except:
        return False
