import asyncio
import os.path
import signal

from bittensor_wallet import wallet
from starlette.websockets import WebSocket

from schemas import WalletData, MinerOptions


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
                await websocket_service.broadcast(output_line)

            await self.running_process.wait()
            return await self.running_process.communicate()
        except Exception as e:
            pass

    async def update_or_clone_miner(self, net_id: int):
        await websocket_service.broadcast(f"Updating or cloning miner")
        await self.run_command(f'./update_miner-{net_id}.sh')

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
        await websocket_service.broadcast("Starting mining process\n")
        await self.update_or_clone_miner(miner_options.net_id)
        await self.regenerate_wallet(miner_options.wallet_data)
        command = f"python -u DistributedTraining/neurons/{miner_options.miner_type.value}.py \
            --netuid {miner_options.net_id} \
            --subtensor.network {miner_options.network} \
            --wallet.name {miner_options.wallet_data.cold_key_name} \
            --wallet.hotkey {miner_options.wallet_data.hot_key_name} \
            --logging.debug \
            --axon.port {miner_options.axon_port} \
            --dht.port {miner_options.dht_port} \
            --dht.announce_ip {miner_options.dht_announce_ip} \
        "
        await self.run_command(command)

    async def stop_mining(self):
        if self.running_process and self.running_process.returncode is None:
            await websocket_service.broadcast(f"Terminating process {self.running_process}")
            os.killpg(self.running_process.pid, signal.SIGTERM)
            await self.running_process.wait()
            await websocket_service.broadcast("Process terminated")
            self.running_process = None
        else:
            await websocket_service.broadcast("No process to terminate")


class WebSocketService:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

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

    async def broadcast(self, message) -> None:
        for connection in self.active_connections:
            await self.send_personal_message(message, connection)

    async def send_initial_msg(
        self, websocket: WebSocket
    ) -> None:
        await self.send_personal_message("It Works", websocket)


websocket_service = WebSocketService()
miner_service = MinerService()
