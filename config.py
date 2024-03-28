# import bittensor as bt
import platform
from enum import Enum
from utils import get_public_ip, get_tao_price

GPU_TYPE_ID = 'NVIDIA RTX A4000'
OS_DISK_SIZE_GB = 20
PERSISTENT_DISK_SIZE_GB = 20
COUNTRY_CODE = 'SK,SE,BE,BG,CA,CZ,NL'
MIN_DOWNLOAD = 70
PORTS = '22/tcp,3000/http,3010/http,3020/http,6006/http,8000/http,8888/http'
MAX_INSTANCE_FOR_SUBNET = 2
VERSION = "1.0.0"
VERSION_URL = "https://drive.google.com/drive/u/5/folders/12bglImLBlEvk0YyIspeASeXe2yBjRlN7"
OS_CORE = "mac" if (name := platform.system()) == "Darwin" else name.lower()


class SubnetType(Enum):
    DISTRIBUTED_TRAINING = 'distributed training 25'
    PROMPTING = 'text prompting 1'
    DATA_UNIVERSE = 'dataverse 13'
    BIT_AGENT = 'bitagent subnet 20'


SUBNET_MAPPER = {
    SubnetType.DISTRIBUTED_TRAINING.value: 25,
    SubnetType.PROMPTING.value: 1,
    SubnetType.DATA_UNIVERSE.value: 13,
    SubnetType.BIT_AGENT.value: 20
}


class MinerType(Enum):
    MINER = 'miner'
    VALIDATOR = 'validator'


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