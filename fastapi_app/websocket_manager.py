import asyncio
from typing import List
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

class ConnectionManager:
    """
    管理 WebSocket 连接的中央类。
    - 维护活跃连接列表。
    - 提供连接、断开和广播消息的方法。
    """
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        """接受一个新的 WebSocket 连接并将其添加到活跃列表。"""
        await websocket.accept()
        self.active_connections.append(websocket)
        print(f"客户端 {websocket.client.host}:{websocket.client.port} 已连接。当前总连接数: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        """从活跃列表中移除一个 WebSocket 连接。"""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            print(f"客户端 {websocket.client.host}:{websocket.client.port} 已断开。当前总连接数: {len(self.active_connections)}")

    async def broadcast(self, message: str):
        """向所有活跃的 WebSocket 连接广播一条消息。"""
        if not self.active_connections:
            print("没有任何客户端连接，无需广播。")
            return

        # 创建一个任务列表来并发地发送消息
        # 遍历列表的副本，以防在迭代时列表被修改
        tasks = [connection.send_text(message) for connection in self.active_connections]
        
        # 等待所有消息发送完成
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 检查并处理发送失败的连接
        failed_connections = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                failed_conn = self.active_connections[i]
                failed_connections.append(failed_conn)
                print(f"向客户端 {failed_conn.client.host}:{failed_conn.client.port} 发送消息失败: {result}")

        # 从主列表中移除已断开或发送失败的连接
        for conn in failed_connections:
            self.disconnect(conn)
            
        print(f"已成功向 {len(tasks) - len(failed_connections)} 个客户端广播消息: '{message}'")

# 创建一个单例的 ConnectionManager 供整个应用使用
manager = ConnectionManager()

# 创建一个 APIRouter 实例，用于定义 WebSocket 路由
router = APIRouter()

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    处理客户端 WebSocket 连接的端点。
    """
    await manager.connect(websocket)
    try:
        # 保持连接打开，可以根据需要处理来自客户端的消息
        while True:
            # 如果不需要处理客户端发来的消息，可以简单地 sleep
            # 如果需要，则使用 await websocket.receive_text()
            await asyncio.sleep(3600) # 保持连接
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        print(f"与客户端 {websocket.client.host}:{websocket.client.port} 的连接发生意外错误并关闭: {e}")
        manager.disconnect(websocket)
