# import bittensor as bt
from enum import Enum

from utils import get_public_ip, get_initial_num_pers, get_tao_price

GPU_TYPE_ID = 'NVIDIA RTX A4000'
OS_DISK_SIZE_GB = 20
PERSISTENT_DISK_SIZE_GB = 20
COUNTRY_CODE = 'SK,SE,BE,BG,CA,CZ,NL'
MIN_DOWNLOAD = 70
PORTS = '22/tcp,3000/http,3010/http,3020/http,6006/http,8000/http,8888/http'

SUBNET_MAPPER = {
    'compute': 25,
}


class MinerType(Enum):
    MINER = 'miner'
    VALIDATOR = 'validator'


class SubnetType(Enum):
    COMPUTE = 'compute'
    STORAGE = 'storage'
    DISTRIBUTED_TRAINING = 'distributed training'
    FINE_TUNING = 'fine tuning'
    MAP_REDUCE = 'map reduce'


INITIAL_PEERS = get_initial_num_pers()
IP_ADDRESS = get_public_ip()
tao_price = get_tao_price()
