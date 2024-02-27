import argparse
import json
from runpod import API  # Adjust the import based on your project structure

def create_pod(pod_config):
    rp = API()
    response = rp.create_on_demand_pod(pod_config)
    resp_json = response.json()
    print(json.dumps(resp_json))  # Print the response to stdout to capture it in the PyQt5 app

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create a RunPod Pod")
    parser.add_argument("--country_code", default="US")
    parser.add_argument("--min_download", type=int, default=20)
    parser.add_argument("--persistent_disk_size_gb", type=int, default=20)
    parser.add_argument("--os_disk_size_gb", type=int, default=20)
    parser.add_argument("--gpu_type_id", default="NVIDIA RTX A4000")
    parser.add_argument("--cloud_type", type=str, default='community')  # Assuming 1 is for Community Cloud
    parser.add_argument("--name", default="Runpod Pytorch")
    parser.add_argument("--ports", default="22,70000,70001,70002,70003,70004,70005,70006,70007,70008")
    parser.add_argument("--image_name", default="runpod/pytorch")
    args = parser.parse_args()

    # Construct the pod_config string using the parsed arguments
    pod_config = f"""
        countryCode: "{args.country_code}",
        minDownload: {args.min_download},
        gpuCount: 1,
        volumeInGb: {args.persistent_disk_size_gb},
        containerDiskInGb: {args.os_disk_size_gb},
        gpuTypeId: "{args.gpu_type_id}",
        cloudType: {args.cloud_type},
        supportPublicIp: true,
        name: "{args.name}",
        dockerArgs: "",
        ports: "{args.ports}",
        volumeMountPath: "/workspace",
        imageName: "{args.image_name}",
        startJupyter: true,
        startSsh: true,
        env: [
            {{
                key: "JUPYTER_PASSWORD",
                value: "Jup1t3R!"
            }},
            {{
                key: "ENABLE_TENSORBOARD",
                value: "1"
            }}
        ]
    """
    create_pod(pod_config)
