from functions.BTC.getWalletTransactionData import run as run_btc
from functions.ETH.getWalletTransactionData import run as run_eth

def main():
    user_input = input("Enter chain (ETH / BTC): ").strip().upper()

    if user_input == "BTC":
        btc_df = run_btc("../datasets/BTC/gambling_address_dataset.csv")
        print("\nBTC DataFrame:\n")
        print(btc_df)
    elif user_input == "ETH":
        eth_df = run_eth("../datasets/ETH/gambling_address_dataset.csv")
        print("\nETH DataFrame:\n")
        print(eth_df)
    else:
        print("Unsupported chain. Please type 'ETH' or 'BTC'.")

if __name__ == "__main__":
    main()