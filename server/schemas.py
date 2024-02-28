from enum import Enum

from pydantic import BaseModel


class MinerType(Enum):
    VALIDATOR = "validator"
    MINER = "miner"


class WalletData(BaseModel):
    cold_key_name: str
    hot_key_name: str = 'default'
    cold_key_mnemonic: str
    hot_key_mnemonic: str


class MinerOptions(BaseModel):
    miner_type: MinerType
    network: str
    net_id: str
    axon_port: int
    dht_port: int
    dht_announce_ip: str
    wallet_data: WalletData
    wandb_key: str
