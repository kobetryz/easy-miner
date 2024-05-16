import asyncio
import os.path
import signal
from datetime import datetime

from bittensor_wallet import wallet
from starlette.websockets import WebSocket

from schemas import WalletData, MinerOptions, MinerType


class MinerService:
    def __init__(self):
        self.running_process = None
        self.miner_options: dict | MinerOptions = {}

    async def run_command(self, command):
        try:
            self.running_process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                preexec_fn=os.setpgrp
            )

            while True:
                output_chunk = await self.running_process.stdout.readline()
                if not output_chunk:
                    break
                output_line = output_chunk.decode("utf-8", errors="replace")
                await websocket_service.broadcast(output_line, end="")

            await self.running_process.wait()
            stdout, stderr = await self.running_process.communicate()
            if stdout:
                await websocket_service.broadcast(stdout.decode("utf-8", errors="replace"), end="")
            if stderr:
                await websocket_service.broadcast(stderr.decode("utf-8", errors="replace"), end="")
        except Exception as e:
            await websocket_service.broadcast(str(e))

    async def update_or_clone_miner(self, net_id: int):
        await websocket_service.broadcast(f"Updating or cloning miner")
        await self.run_command(f'./update_miner-{self.parent.net_id}.sh')

    @staticmethod
    async def regenerate_wallet(wallet_data: WalletData):
        if os.path.exists(os.path.expanduser(f"~/.bittensor/wallets/{wallet_data.cold_key_name}")):
            await websocket_service.broadcast(f"Wallet already exists")
            return
        await websocket_service.broadcast(f"Regenerating wallet")
        new_wallet = wallet(name=wallet_data.cold_key_name, path='~/.bittensor/wallets')
        new_wallet.regen_coldkey(mnemonic=wallet_data.cold_key_mnemonic, use_password=False)
        new_wallet.regen_hotkey(mnemonic=wallet_data.hot_key_mnemonic, use_password=False)
        await websocket_service.broadcast(f"Wallet regenerated")

    async def wandb_login(self, wandb_key: str):
        await websocket_service.broadcast(f"Logging into wandb")
        await self.run_command(f'wandb login {wandb_key}')
        await websocket_service.broadcast(f"Logged into wandb")

    async def start_mining(self, miner_options: MinerOptions):
        self.miner_options = miner_options
        await self.wandb_login(miner_options.wandb_key)
        await websocket_service.broadcast("Starting mining process")
        await self.update_or_clone_miner(miner_options.net_id)
        await self.regenerate_wallet(miner_options.wallet_data)
        command = self.get_running_args(miner_options)
        await self.run_command(command)

    @staticmethod
    def get_running_args(minner_options: MinerOptions):
        base_command = "python -u {script_path} --wallet.name {wallet_name} --wallet.hotkey {hotkey}"

        script_paths = {
            25: f"DistributedTraining/neurons/{minner_options.miner_type.value}.py",
            1: f"prompting/neurons/{minner_options.miner_type.value}.py",
            13: f"data-universe/neurons/{minner_options.miner_type.value}.py",
            20: f"bitagent_subnet/neurons/{minner_options.miner_type.value}.py",
        }

        extra_args = {
            25: f"--netuid {minner_options.net_id} --subtensor.network {minner_options.network} --logging.debug"
                f" --axon.port {minner_options.axon_port} --axon.ip {minner_options.dht_announce_ip} "
                f"--axon.external_port {minner_options.axon_port} --flask.host_address 127.0.0.1 --flask.host_port 8001",
            1: f"--netuid {minner_options.net_id} --subtensor.network {minner_options.network} --logging.debug" + (
                " --neuron.device cuda" if minner_options.miner_type != MinerType.MINER else ""),
            20: f"--netuid {minner_options.net_id} --subtensor.network {minner_options.network} --axon.port {minner_options.axon_port}"
        }

        if minner_options.net_id not in script_paths:
            return None

        command = base_command.format(script_path=script_paths[minner_options.net_id],
                                      wallet_name=minner_options.wallet_data.cold_key_name,
                                      hotkey=minner_options.wallet_data.hot_key_name)

        if minner_options.net_id in extra_args:
            command += " " + extra_args[minner_options.net_id]

        return command

    async def stop_mining(self):
        if self.is_running():
            await websocket_service.broadcast(f"Terminating process {self.running_process}")
            os.killpg(self.running_process.pid, signal.SIGTERM)
            await self.running_process.wait()
            await websocket_service.broadcast("Process terminated")
            self.running_process = None
        else:
            await websocket_service.broadcast("No process to terminate")

    def is_running(self):
        return self.running_process and self.running_process.returncode is None


class WebSocketService:
    def __init__(self):
        self.active_connections: list[WebSocket] = []
        self.logs = MaxSizeList(100)

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self.active_connections.append(websocket)
        await self.send_initial_msg(websocket)

    def disconnect(self, websocket: WebSocket) -> None:
        self.active_connections.remove(websocket)

    async def send_personal_message(
        self,
        message: str,
        websocket: WebSocket,
        attempt: int = 0,
    ):
        try:
            await websocket.send_text(message)
        except Exception as e:
            if attempt < 3:
                await asyncio.sleep(0.5)
                return await self.send_personal_message(
                    message, websocket, attempt + 1
                )

    async def broadcast(self, message, end="\n") -> None:
        line = message + end
        index = line.rfind('|')
        if index != -1:
            line = line[index + 2:]
        line = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | {line}"
        for connection in self.active_connections:
            await self.send_personal_message(line, connection)
        self.logs.append(line)

    async def send_initial_msg(
        self, websocket: WebSocket
    ) -> None:
        for line in self.logs.get_list():
            await self.send_personal_message(line, websocket)


class MaxSizeList:
    def __init__(self, max_size):
        self.max_size = max_size
        self.list = [f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | It works!\n"]

    def append(self, item):
        self.list.append(item)
        if len(self.list) > self.max_size:
            self.list.pop(0)

    def get_list(self):
        return self.list


websocket_service = WebSocketService()
miner_service = MinerService()
