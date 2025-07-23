# coap_task.py

from celery import shared_task
from aiocoap import resource, Message, Context, Code
import asyncio
import redis
from celery.signals import worker_ready


# Redis pub config
redis_client = redis.Redis(host='localhost', port=6379, db=0)

class PerfumeSelectorResource(resource.Resource):
    async def render_post(self, request):
        try:
            payload = request.payload.decode()
            print(f"📥 CoAP Received payload: {payload}")

            # Parse payload dạng "perfume_id=P005"
            key, value = payload.strip().split("=")
            if key == "perfume_id":
                redis_client.publish('perfume_selector_channel', value)
                print(f"✅ Published perfume_id={value} to Redis")

            return Message(code=Code.CHANGED, payload=b"ACK from CoAP")
        except Exception as e:
            print(f"❌ Error handling CoAP POST: {e}")
            return Message(code=Code.BAD_REQUEST, payload=b"Error")

@shared_task
def run_coap_server():
    async def main():
        root = resource.Site()
        root.add_resource(['select'], PerfumeSelectorResource())
        await Context.create_server_context(root)
        print("🚀 CoAP server started on /select")
        await asyncio.get_running_loop().create_future()

    asyncio.run(main())

@worker_ready.connect
def at_worker_start(sender, **kwargs):
    print("✅ Celery worker ready — Starting CoAP...")
    run_coap_server.delay()