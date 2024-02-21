# import os
# import psutil
# import subprocess
# import platform

# def get_cpu_usage():
#     # Get CPU usage as a percentage
#     cpu_usage = psutil.cpu_percent(interval=1)
#     return f"CPU Usage: {cpu_usage}%"

# def get_gpu_usage():
#     try:
#         if platform.system() == 'Linux':
#             # Check if intel_gpu_top is available
#             subprocess.run(['which', 'intel_gpu_top'], check=True)

#             # Run intel_gpu_top command to get GPU information
#             result = subprocess.run(['sudo', 'intel_gpu_top', '-- ', '1', '1'], capture_output=True, text=True)

#             # Extract GPU usage from the output
#             gpu_usage_line = [line for line in result.stdout.split('\n') if 'render busy' in line][0]
#             gpu_usage = gpu_usage_line.split(':')[-1].strip()
#             return f"GPU Usage: {gpu_usage}"
#         elif platform.system() == 'Darwin':
#             # Run an AppleScript to get GPU usage on macOS
#             script = 'tell application "Activity Monitor" to get the value of attribute "GPU usage" of the first window'
#             result = subprocess.run(['osascript', '-e', script], capture_output=True, text=True)
#             gpu_usage = result.stdout.strip()
#             return f"GPU Usage: {gpu_usage}%"
#         else:
#             return "GPU monitoring is only supported on Linux and macOS systems with Intel GPUs."

#     except Exception as e:
#         return f"Error retrieving GPU usage: {e}"

# if __name__ == "__main__":
#     # Get and print CPU usage
#     cpu_info = get_cpu_usage()
#     print(cpu_info)

#     # Get and print GPU usage
#     gpu_info = get_gpu_usage()
#     print(gpu_info)

# https://intel.github.io/intel-extension-for-pytorch/xpu/1.13.120+xpu/tutorials/examples.html

import os
import psutil
import subprocess
import platform
import time
import torch

# from config import configure_logger

# cpu_gpu = configure_logger('test_logging.log')
matrix = 5000


def get_cpu_usage():
    cpu_usage = psutil.cpu_percent(interval=1)
    return f"CPU Usage: {cpu_usage}%"


def get_gpu_usage():
    try:
        if platform.system() == 'Linux':
            subprocess.run(['which', 'intel_gpu_top'], check=True)
            result = subprocess.run(['sudo', 'intel_gpu_top', '-- ', '1', '1'], capture_output=True, text=True)
            gpu_usage_line = [line for line in result.stdout.split('\n') if 'render busy' in line][0]
            gpu_usage = gpu_usage_line.split(':')[-1].strip()
            return f"GPU Usage: {gpu_usage}"
        elif platform.system() == 'Darwin':
            result = subprocess.run(['system_profiler', 'SPDisplaysDataType'], capture_output=True, text=True)

            # Extract the GPU usage information
            # print(result)
            gpu_info = result.stdout.split("Graphics/Displays:", 1)[-1]
            gpu_usage = [line.strip() for line in gpu_info.splitlines() if 'Chipset Model' in line][0]
            
            return f"GPU Usage: {gpu_usage}"
        else:
            return "GPU monitoring is only supported on Linux and macOS systems with Intel GPUs."
    except Exception as e:
        return f"Error retrieving GPU usage: {e}"


def matrix_multiply_cpu():
    # Perform a simple matrix multiplication on CPU
    matrix_a = torch.rand((matrix, matrix))
    matrix_b = torch.rand((matrix, matrix))
    result = torch.matmul(matrix_a, matrix_b)


def matrix_multiply_gpu():
    try:
        # Perform a simple matrix multiplication on Intel GPU using OpenCL
        matrix_a = torch.rand((matrix, matrix), device='opencl:0')
        matrix_b = torch.rand((matrix, matrix), device='opencl:0')
        result = torch.matmul(matrix_a, matrix_b)
    except Exception as e:
        return f"Error performing GPU matrix multiplication: {e}"


if __name__ == "__main__":
    # Measure CPU usage
    start_time_cpu = time.time()
    # cpu_gpu.info(f"Cpu Start")
    cpu_info = get_cpu_usage()
    matrix_multiply_cpu()
    end_time_cpu = time.time()
    print(cpu_info)
    print(f"Time taken on CPU: {end_time_cpu - start_time_cpu} seconds")
    # cpu_gpu.info(f"CPU Time: {end_time_cpu - start_time_cpu}")

    # Measure GPU usage
    start_time_gpu = time.time()
    # cpu_gpu.info(f"GPU Start")
    gpu_info = get_gpu_usage()
    matrix_multiply_gpu()
    end_time_gpu = time.time()
    print(gpu_info)
    print(f"Time taken on GPU: {end_time_gpu - start_time_gpu} seconds")
    # cpu_gpu.info(f"{end_time_gpu - start_time_gpu}")