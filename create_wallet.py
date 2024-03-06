import argparse
import bittensor as bt
from substrateinterface import Keypair


def create_wallet_with_password(wallet_name, wallet_path, password="Hello world"):
    wallet = bt.wallet(name=wallet_name, path=wallet_path)
    hk_mnemonic = Keypair.generate_mnemonic()
    hk_keypair = Keypair.create_from_mnemonic(hk_mnemonic)
    wallet._hotkey = hk_keypair
    wallet.hotkey_file.set_keypair(hk_keypair, encrypt=True, password=password)
    ck_mnemonic = Keypair.generate_mnemonic()
    ck_keypair = Keypair.create_from_mnemonic(ck_mnemonic)
    wallet._coldkey = ck_keypair
    wallet.coldkey_file.set_keypair(ck_keypair, encrypt=True, password=password)
    wallet.set_coldkeypub(ck_keypair)


def create_wallet(wallet_name, wallet_path):
    wallet = bt.wallet(name=wallet_name, path=wallet_path)
    # wallet.create_if_non_existent()
    wallet.create_new_hotkey(use_password=False)
    wallet.create_new_coldkey(use_password=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Create a new Bittensor wallet.')
    parser.add_argument('--wallet_name', type=str, required=True, help='Name of the wallet')
    parser.add_argument('--wallet_path', type=str, required=True, help='Path to store the wallet')
    parser.add_argument('--password', type=str, required=False, help='Password to encrypt the wallet file.')

    args = parser.parse_args()
    create_wallet(args.wallet_name, args.wallet_path)
