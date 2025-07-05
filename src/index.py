from functions.BTC.getWalletTransactionData import run as run_btc
from functions.ETH.getWalletTransactionData import run as run_eth
from functions.ETH.getContractAbi import is_contract, get_contract_abi

def main():
    user_input = input("Enter chain (ETH / BTC): ").strip().upper()

    if user_input == "BTC":
        btc_df = run_btc("../datasets/BTC/gambling_address_dataset.csv")
        print("\nBTC DataFrame:\n")
        print(btc_df)
    elif user_input == "ETH":
        eth_df, all_txs = run_eth("../datasets/ETH/gambling_address_dataset.csv")
        print("\nETH DataFrame:\n")
        print(eth_df)

        print("\nSmart Contracts Interacted With:")
        seen_contracts = set()

        # if the to_address is a smart contract, then get the abi to check the functions is it contains gamble attributes or not
        for wallet, txs in all_txs.items():
            for tx in txs:
                to_addr = tx.get("to", "").lower()
                if to_addr and to_addr not in seen_contracts:
                    if is_contract(to_addr):
                        print(f"\n{wallet} interacted with smart contract: {to_addr}")
                        abi = get_contract_abi(to_addr)
                        if abi:
                            print(f"ABI for {to_addr}:\n{abi}\n")
                        seen_contracts.add(to_addr)
    else:
        print("Unsupported chain. Please type 'ETH' or 'BTC'.")

if __name__ == "__main__":
    main()