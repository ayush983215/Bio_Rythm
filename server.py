import asyncio

import websockets

import subprocess

import socket



print("⚡ Starting WebSocket Server...")



host_ip = socket.gethostbyname(socket.gethostname())

port = 9001  # Change if needed



async def send_prediction(websocket, path):  # Ensure 'path' is included

    print("[✅ Client Connected]")

    try:

        while True:

            process = subprocess.Popen(['python', 'prediction.py'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

            output, error = process.communicate()



            if output:

                print(f"[📤 Sending]: {output.strip()}")

                await websocket.send(output.strip())



            await asyncio.sleep(5)

    except websockets.exceptions.ConnectionClosed:

        print("[❌ Client Disconnected]")

    except Exception as e:

        print(f"[🔥 Error] {e}")



async def main():

    print(f"✅ WebSocket server running on ws://{host_ip}:{port}")

    server = await websockets.serve(send_prediction, "0.0.0.0", port)  # No changes here

    await server.wait_closed()



asyncio.run(main())