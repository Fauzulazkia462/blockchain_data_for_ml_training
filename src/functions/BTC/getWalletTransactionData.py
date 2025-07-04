import time
import pandas as pd
import requests
from collections import Counter, defaultdict
from datetime import datetime, timezone
from helpers import (
    read_addresses_from_csv,
    is_night_tx,
    std,
    most_common,
)

BLOCKSTREAM_API = "https://blockstream.info/api"

def _blockstream_get(url: str) -> dict | list:
    for attempt in range(3):
        r = requests.get(url, timeout=20)
        if r.ok:
            return r.json()
        time.sleep(2 ** attempt)
    r.raise_for_status()
    return {}

def fetch_btc_txs(addr: str, max_pages: int = 20) -> list[dict]:
    txs: list[dict] = []
    url = f"{BLOCKSTREAM_API}/address/{addr}/txs"
    for _ in range(max_pages):
        page = _blockstream_get(url)
        if not page:
            break
        txs.extend(page)
        last_txid = page[-1]["txid"]
        url = f"{BLOCKSTREAM_API}/address/{addr}/txs/chain/{last_txid}"
    return txs

def _btc_tx_amount_relative(tx: dict, wallet: str) -> float:
    satoshis_in = 0
    satoshis_out = 0
    for vin in tx["vin"]:
        if "prevout" in vin and wallet in vin["prevout"].get("scriptpubkey_address", ""):
            satoshis_in += vin["prevout"]["value"]
    for vout in tx["vout"]:
        if wallet in vout.get("scriptpubkey_address", ""):
            satoshis_out += vout["value"]
    return (satoshis_out - satoshis_in) / 1e8

def _btc_counterparties(tx: dict, wallet: str) -> set[str]:
    all_in = {
        vin["prevout"]["scriptpubkey_address"]
        for vin in tx["vin"]
        if "prevout" in vin
    }
    
    all_out = {
        vout.get("scriptpubkey_address")
        for vout in tx["vout"]
        if "scriptpubkey_address" in vout
    }

    all_out.discard(None)

    if wallet in all_in:
        return all_out - {wallet}
    if wallet in all_out:
        return all_in - {wallet}
    return set()

def extract_btc_features(txs: list[dict], wallet: str) -> dict:
    if not txs:
        return {}
    dates, amounts, blocks = [], [], []
    counterparties: set[str] = set()
    night_tx_count = 0

    for tx in txs:
        ts = tx["status"].get("block_time") or int(time.time())
        dates.append(datetime.fromtimestamp(ts, timezone.utc).strftime("%Y-%m-%d"))
        amounts.append(_btc_tx_amount_relative(tx, wallet))
        blocks.append(tx["status"].get("block_height", 0))
        counterparties.update(_btc_counterparties(tx, wallet))
        if is_night_tx(ts):
            night_tx_count += 1

    block_counts = Counter(blocks)
    max_per_block = max(block_counts.values())
    min_per_block = min(block_counts.values())
    unique_blocks = len(block_counts)

    same_day_in_out = 0
    by_date = defaultdict(list)
    for tx, d in zip(txs, dates):
        by_date[d].append(tx)
    for items in by_date.values():
        ins, outs = False, False
        for tx in items:
            net = _btc_tx_amount_relative(tx, wallet)
            if net > 0:
                ins = True
            if net < 0:
                outs = True
        if ins and outs:
            same_day_in_out += 1

    feats = dict(
        chain="BTC",
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

def run(csv_path="../datasets/BTC/gambling_address_dataset.csv"):
    addresses = read_addresses_from_csv(csv_path)
    print(f"Found {len(addresses)} addresses")

    rows = []
    for addr in addresses:
        try:
            if not addr.lower().startswith("0x"):
                print(f"(BTC) Fetching {addr}")
                txs = fetch_btc_txs(addr)
                if txs:
                    rows.append(extract_btc_features(txs, addr))
        except Exception as exc:
            print(f"Error with {addr}: {exc}")

    df = pd.DataFrame(rows)
    pd.set_option("display.max_columns", None)
    pd.set_option("display.width", 150)
    return df

if __name__ == "__main__":
    run()
