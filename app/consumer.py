import aio_pika
import aiormq
import asyncio
import json
import os

from dotenv import load_dotenv

load_dotenv()

RABBITMQ_URL = os.getenv("RABBITMQ_URL")
QUEUE_NAME = os.getenv("QUEUE_NAME", "user_events_queue")
USE_EXCHANGE = os.getenv("USE_EXCHANGE", "true").lower() in ("1", "true", "yes")


currentUser = None

if not RABBITMQ_URL:
    raise RuntimeError("RABBITMQ_URL is not set. Export it or add it to a .env file.")

async def consume():
    global currentUser
    print(f"Connecting to RabbitMQ at {RABBITMQ_URL}")
    connection = await aio_pika.connect(RABBITMQ_URL)

    async with connection:
        channel = await connection.channel()
        await channel.set_qos(prefetch_count=1)

        queue = await channel.declare_queue(QUEUE_NAME, durable=True)

        if USE_EXCHANGE:
            
            try:
                await queue.bind("user_events")
                print(f"Bound queue '{QUEUE_NAME}' to exchange name 'user_events' (no redeclare)")
            except Exception as exc:
                print("Failed to bind to exchange name 'user_events'; continuing to listen to queue only:", exc)

        print(f"Waiting for messages on '{QUEUE_NAME}'...")

        try:
            async with queue.iterator() as q:
                async for message in q:
                    async with message.process():
                        try:
                            raw = message.body
                            if isinstance(raw, (bytes, bytearray)):
                                raw = raw.decode("utf-8")

                            payload = json.loads(raw)

                            user_id = None
                            event_type = None
                            data = None
                            if isinstance(payload, dict):
                                event_type = payload.get("event_type")
                                data = payload.get("data")

                                if event_type == "user_login": # on user login event, set currentUser
                                    user_id = payload.get("user_id")
                                    if not user_id and isinstance(data, dict):
                                        user_id = data.get("user_id")

                                    if user_id:
                                        currentUser = user_id
                                        print("Set currentUser=", currentUser)
                                
                                if event_type == "user_logout": # on user logout event, clear currentUser
                                    user_id = payload.get("user_id")
                                    if not user_id and isinstance(data, dict):
                                        user_id = data.get("user_id")

                                    if user_id:
                                        currentUser = "691c8bf8d691e46d00068bf3" #default user
                                        print("user logged out\nSet default currentUser=", currentUser)

                                if event_type == "user_deletion":  # on user deletion event, clear currentUser
                                    user_id = payload.get("user_id")
                                    if not user_id and isinstance(data, dict):
                                        user_id = data.get("user_id")

                                    if user_id:
                                        currentUser = "691c8bf8d691e46d00068bf3" #default user
                                        print("user deleted\nSet default currentUser=", currentUser)


                                    

                            print("Received event=", event_type, "data=", data)
                        except json.JSONDecodeError as e:
                            print("Invalid JSON in message body:", e)
                        except Exception as e:
                            print("Failed to process message:", e)
        except asyncio.CancelledError:
            print("Consumer cancelled")


if __name__ == "__main__":
    try:
        asyncio.run(consume())
    except KeyboardInterrupt:
        print("Interrupted by user")
