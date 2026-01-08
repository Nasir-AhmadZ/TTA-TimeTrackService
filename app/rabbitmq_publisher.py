import pika
import json
import os
from typing import Dict, Any
from datetime import datetime, timezone

class RabbitMQPublisher:
    def __init__(self, rabbitmq_url: str = None):
        self.rabbitmq_url = rabbitmq_url or os.getenv("RABBIT_URL")
        self.connection = None
        self.channel = None
        
    def connect(self):
        try:
            if not self.rabbitmq_url:
                print("WARNING: RABBIT_URL not set; skipping RabbitMQ connection")
                return False

            params = pika.URLParameters(self.rabbitmq_url)
            self.connection = pika.BlockingConnection(params)
            self.channel = self.connection.channel()

            self.channel.exchange_declare(exchange='notificiations_topic', exchange_type='topic')
            print("Connected to RabbitMQ")
            return True
        except Exception as e:
            print(f"ERROR: Failed to connect to RabbitMQ: {e}")
            # Do not raise here to allow the application to start without RabbitMQ
            return False

    def close(self):
        try:
            if self.connection and not self.connection.is_closed:
                self.connection.close()
                print("RabbitMQ connection closed")
        except Exception as e:
            print(f"ERROR: Failed to close RabbitMQ connection: {e}")

    def publish_event(self, event_type: str, routing_key: str, currentUser: str, data: Dict[str, Any]) -> bool:
        try:
            if not self.channel or self.connection.is_closed:
                if not self.connect():
                    return False
            
            message = {
                "event_type": event_type,
                "currentUser": currentUser,
                "timestamp": datetime.now().isoformat(),
                "data": data
            }

            #pulish message to queue 
            self.channel.basic_publish(
                exchange='notificiations_topic',
                routing_key=routing_key,
                body=json.dumps(message),
                properties=pika.BasicProperties(
                    delivery_mode=2,# make message persistent
                    content_type='application/json'                  
                )
            )

            print(f"Published event: {event_type}")
            return True

        except Exception as e:
            print(f"ERROR: Failed to publish event {event_type}: {e}")
            # Attempt to reconnect once
            try:
                self.close()
                self.connect()
            except:
                pass
            return False


    # publish user login
    def createNotification(self, event_type: str, currentUser: str, routing_key: str, data: dict):
        return self.publish_event(event_type, routing_key, currentUser, {
            "event_type": event_type,
            "currentUser": currentUser,
            "timestamp": datetime.now().isoformat(),
            "data": data
        })

_publisher = RabbitMQPublisher()

def get_rabbitmq_publisher() -> RabbitMQPublisher:
    global _publisher
    if _publisher is None:
        _publisher = RabbitMQPublisher()
    return _publisher