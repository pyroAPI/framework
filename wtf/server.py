import asyncio
from httphandler import RequestHandler
from http_objects import Response

async def handle_client(reader, writer, router=None):
    """Handle client connection with optional router"""
    addr = writer.get_extra_info("peername")
    print(f"🔌 Connected by {addr}")

    handler = RequestHandler(writer, router)

    try:
        # Read data in chunks until we have a complete request
        while not reader.at_eof():
            data = await reader.read(1024)
            if not data:
                break
            
            handler.feed_data(data)
            
            # Check if we've received a complete message
            if handler._message_complete:
                # Wait for the response to be sent
                await handler.response_sent.wait()
                break
                
        # If we exit the loop without completing the message, it might be an incomplete request
        if not handler._message_complete:
            print("⚠️ Incomplete request received")
            error_response = Response.error("Incomplete request", 400)
            response_bytes = error_response.to_bytes()
            writer.write(response_bytes)
            
    except ConnectionResetError:
        print(f"🔌 Connection reset by {addr}")
    except asyncio.TimeoutError:
        print(f"⏰ Connection timeout for {addr}")
        error_response = Response.error("Request timeout", 408)
        response_bytes = error_response.to_bytes()
        writer.write(response_bytes)
    except Exception as e:
        print(f"❌ Error handling client {addr}: {e}")
        try:
            error_response = Response.error("Internal Server Error", 500)
            response_bytes = error_response.to_bytes()
            writer.write(response_bytes)
        except:
            pass
    finally:
        try:
            await writer.drain()
            writer.close()
            await writer.wait_closed()
            print(f"🔒 Connection to {addr} closed")
        except Exception as e:
            print(f"⚠️ Error closing connection to {addr}: {e}")