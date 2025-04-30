import asyncio
import websockets
import json
import subprocess
import paho.mqtt.publish as publish
from datetime import datetime

BROKER ='158.173.101.159'
PORT = 1883
TOPIC = 'relay/scheduler'
initial_schedule = {'onTime': None, 'offTime':None}
async def to_handle_connection(websocket,path):
    try:
        async for message in websocket:
             received_data= json.loads(message)
             onTime = received_data['onTime']
             off_time = received_data['offTime']
             initial_schedule['onTime'] = onTime
             initial_schedule['offTime'] = off_time
             await websocket.send(f"Scheduled: ON at {onTime}, OFF at {off_time}")
             print(f"scheduled : ON at {onTime}, OFF at {off_time}")
    except Exception as e:
        await websocket.send(f"Error: {str(e)}")
        print("Failed to send info via websocket")

async def check_schedule():
    while True:
        now = datetime.now().strftime('%H:%M')
        if initial_schedule['onTime'] == now:
            print(f"Triggering ON at {now}")
            publish.single(
                topic=TOPIC,
                payload='1',
                hostname=BROKER,
                port=PORT,
                retain=False
            )
        if initial_schedule['offTime'] == now:
            print(f"Triggering OFF at {now}")
            publish.single(
                topic=TOPIC,
                payload='0',
                hostname=BROKER,
                port=PORT,
                retain=False
            )
        await asyncio.sleep(30)  # Check every 30 seconds

async def main():
    server = await websockets.serve(to_handle_connection, "localhost", 8765)
    print("WebSocket server running on ws://localhost:8765")
    asyncio.create_task(check_schedule())
    await server.wait_closed()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Server stopped")
