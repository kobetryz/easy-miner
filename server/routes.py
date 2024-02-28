from fastapi import APIRouter, WebSocket
from starlette.background import BackgroundTasks
from starlette.websockets import WebSocketDisconnect

from schemas import MinerOptions
from service import websocket_service, miner_service

router = APIRouter(tags=["main"])


@router.get("/")
async def read_root():
    return {"it's": "works"}


@router.post("/mine")
async def mine(miner_options: MinerOptions, background_tasks: BackgroundTasks):
    background_tasks.add_task(miner_service.start_mining, miner_options)
    return {"message": "Mining process started in the background."}


@router.post("/stop-mine")
async def stop_mine():
    await miner_service.stop_mining()
    return {"message": "Mining process stopped."}


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket_service.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect as e:
        pass
    finally:
        websocket_service.disconnect(websocket)
