# main.py

import asyncio
from server import handle_client
from middleware import logger_middleware, auth_middleware
from app import app  # ✅ Import the router instance with all user-defined routes

async def main():
    app.add_middleware(logger_middleware)
    app.add_middleware(auth_middleware)

    # Print all registered routes for debugging
    print("📌 Registered routes:")
    for r in app.list_routes():
        print(f" → {r['method']} {r['pattern']}")

    server = await asyncio.start_server(
        lambda r, w: handle_client(r, w, router=app),
        host="127.0.0.1",
        port=8080
    )
    print("🚀 Server running at http://127.0.0.1:8080")
    async with server:
        await server.serve_forever()

if __name__ == "__main__":
   
    try:
        asyncio.run(main())

    except KeyboardInterrupt:
        print("\n🛑 Server stopped manually.")
