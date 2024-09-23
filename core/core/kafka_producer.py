import json
import logging

from confluent_kafka import Producer

logger = logging.getLogger(__name__)


class KafkaProducer:
    def __init__(self, bootstrap_servers: str):
        self.producer = Producer({'bootstrap.servers': bootstrap_servers})

    def send_message(self, topic: str, key: str, value: dict):
        try:
            message = json.dumps(value).encode('utf-8')
            self.producer.produce(topic=topic, key=key.encode('utf-8'), value=message)
            self.producer.flush()
        except Exception as e:
            logger.error(f"Failed to send message: {e}", exc_info=True)
