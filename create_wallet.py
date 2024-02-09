import argparse
import bittensor as bt    

 
def create_wallet(wallet_name, wallet_path):
    wallet = bt.wallet(name=wallet_name, path=wallet_path)
    # wallet.create_if_non_existent()
    wallet.create_new_hotkey(use_password=False)
    wallet.create_new_coldkey(use_password = False)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Create a new Bittensor wallet.')
    parser.add_argument('--wallet_name', type=str, required=True, help='Name of the wallet')
    parser.add_argument('--wallet_path', type=str, required=True, help='Path to store the wallet')

    args = parser.parse_args()
    create_wallet(args.wallet_name, args.wallet_path)