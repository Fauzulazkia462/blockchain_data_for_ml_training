import os
import csv
import numpy as np
import pandas as pd
import requests
from collections import Counter, defaultdict
from datetime import datetime, timezone
from dotenv import load_dotenv
from helpers import (
    read_addresses_from_csv,
    is_night_tx,
    std,
    most_common,
)

load_dotenv()

ETHERSCAN_API = "https://api.etherscan.io/api"
ETHERSCAN_KEY = os.getenv("ETHERSCAN_API_KEY")

def fetch_eth_txs(addr: str) -> list[dict]:
    params = dict(
        module="account",
        action="txlist",
        address=addr,
        startblock=0,
        endblock=99999999,
        sort="asc",
        apikey=ETHERSCAN_KEY,
    )
    r = requests.get(ETHERSCAN_API, params=params, timeout=30)
    r.raise_for_status()
    data = r.json()
    return data["result"] if data.get("status") == "1" else []

def extract_eth_features(txs: list[dict], wallet: str) -> dict:
    if not txs:
        return {}
    wallet_lower = wallet.lower()
    dates = [
        datetime.fromtimestamp(int(tx["timeStamp"]), timezone.utc).strftime("%Y-%m-%d")
        for tx in txs
    ]
    amounts = [float(tx["value"]) / 1e18 for tx in txs]
    blocks = [int(tx["blockNumber"]) for tx in txs]
    counterparties = {
        (tx["from"] if tx["to"].lower() == wallet_lower else tx["to"]).lower()
        for tx in txs
    }
    night_tx_count = sum(is_night_tx(int(tx["timeStamp"])) for tx in txs)

    block_counts = Counter(blocks)
    max_per_block = max(block_counts.values())
    min_per_block = min(block_counts.values())
    unique_blocks = len(block_counts)

    same_day_in_out = 0
    by_date = defaultdict(list)
    for tx, d in zip(txs, dates):
        by_date[d].append(tx)
    for items in by_date.values():
        ins = any(tx["to"].lower() == wallet_lower for tx in items)
        outs = any(tx["from"].lower() == wallet_lower for tx in items)
        if ins and outs:
            same_day_in_out += 1

    feats = dict(
        chain="ETH",
        address=wallet,
        tx_total=len(txs),
        avg_tx_per_day=round(len(txs) / len(set(dates)), 2),
        avg_tx_per_block=round(len(txs) / unique_blocks, 4) if unique_blocks else 0,
        max_tx_per_block=max_per_block,
        min_tx_per_block=min_per_block,
        std_tx_amount=round(std(amounts), 6),
        tx_between_00_04=round(night_tx_count / len(txs), 4),
        num_unique_counterparties=len(counterparties),
        same_day_deposit_withdraw=int(same_day_in_out > 0),
        most_common_amount=most_common(amounts),
    )
    return feats

def main(csv_path="./gambling_address_dataset.csv"):
    addresses = read_addresses_from_csv(csv_path)
    print(f"Found {len(addresses)} addresses")

    rows = []
    for addr in addresses:
        try:
            if addr.lower().startswith("0x"):
                print(f"(ETH) Fetching {addr}")
                txs = fetch_eth_txs(addr)
                if txs:
                    rows.append(extract_eth_features(txs, addr))
        except Exception as exc:
            print(f"Error with {addr}: {exc}")

    df = pd.DataFrame(rows)
    pd.set_option("display.max_columns", None)
    pd.set_option("display.width", 150)
    print("\nFeature DataFrame:\n")
    print(df)

if __name__ == "__main__":
    main()
