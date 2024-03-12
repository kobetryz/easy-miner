# import bittensor as bt
from enum import Enum

from utils import get_public_ip, get_tao_price

GPU_TYPE_ID = 'NVIDIA RTX A4000'
OS_DISK_SIZE_GB = 20
PERSISTENT_DISK_SIZE_GB = 20
COUNTRY_CODE = 'SK,SE,BE,BG,CA,CZ,NL'
MIN_DOWNLOAD = 70
PORTS = '22/tcp,3000/http,3010/http,3020/http,6006/http,8000/http,8888/http'

SUBNET_MAPPER = {
    'distributed training': 25,
}


class MinerType(Enum):
    MINER = 'miner'
    VALIDATOR = 'validator'


class SubnetType(Enum):
    DISTRIBUTED_TRAINING = 'distributed training'
    COMPUTE = 'compute'
    STORAGE = 'storage'
    FINE_TUNING = 'fine tuning'
    MAP_REDUCE = 'map reduce'


class NetworkType(Enum):
    FINNEY = "finney"
    TEST = "test"


DIRECTORY_MAPPER = {
    25: 'DistributedTraining',
    1: 'prompting',
    13: 'data-universe',
    20: 'bitagent_subnet',
}

IP_ADDRESS = get_public_ip()
tao_price = get_tao_price()

CHECK_UPDATES_TIME = 12*60*60*1000  # 12 hours in milliseconds