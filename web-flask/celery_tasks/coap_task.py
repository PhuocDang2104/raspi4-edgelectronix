from aiocoap import resource, Message, Context, Code
import asyncio
import redis
import threading
from celery.signals import worker_ready
from celery_app import celery


# Redis pub config
redis_client = redis.Redis(host='localhost', port=6379, db=0)

# CoAP Resource để nhận POST request tại /select
class PerfumeSelectorResource(resource.Resource):
    async def render_post(self, request):
        try:
            payload = request.payload.decode()
            print(f"📥 CoAP Received payload: {payload}")

            key, value = payload.strip().split("=")
            if key == "perfume_id":
                redis_client.publish('perfume_selector_channel', value)
                print(f"✅ Published perfume_id={value} to Redis")

            return Message(code=Code.CHANGED, payload=b"ACK from CoAP")
        except Exception as e:
            print(f"❌ Error handling CoAP POST: {e}")
            return Message(code=Code.BAD_REQUEST, payload=b"Error")

# Hàm chạy CoAP server trong thread phụ với event loop riêng
def run_coap_server():
    async def main():
        root = resource.Site()
        root.add_resource(['select'], PerfumeSelectorResource())
        await Context.create_server_context(root)
        print("🚀 CoAP server started on /select")
        await asyncio.get_running_loop().create_future()  # Keeps server alive

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(main())

# Khi Celery worker sẵn sàng, kích hoạt CoAP server
@worker_ready.connect
def at_worker_start(sender, **kwargs):
    print("✅ Celery worker ready — Starting CoAP server...")
    threading.Thread(target=run_coap_server, daemon=True).start()
