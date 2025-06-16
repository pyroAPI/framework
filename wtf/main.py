import asyncio
from server import handle_client
from router import default_router as router
from middleware import logger_middleware
from middleware import auth_middleware

async def main():
    # Register middleware
    router.add_middleware(logger_middleware)
    router.add_middleware(auth_middleware)

    # Start server with router passed to handler
    server = await asyncio.start_server(
        lambda r, w: handle_client(r, w, router), "127.0.0.1", 8080
    )

    print("🚀 Server running at http://127.0.0.1:8080")
    async with server:
        await server.serve_forever()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Server stopped manually.")
