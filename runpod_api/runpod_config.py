import json
import gc
from runpod import API

api = API()
response = api.get_gpu_types()
GPU_DICT = response.json()['data']['gpuTypes']
GPU_DICT = {gpu['displayName']:gpu for gpu in GPU_DICT}

GPU_LIST_TO_USE = ['RTX 3090','RTX A4000', 'RTX 4090', 'RTX A4500' ,'RTX A5000']  
print(GPU_LIST_TO_USE)
