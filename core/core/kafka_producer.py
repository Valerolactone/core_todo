import json

from aiokafka import AIOKafkaProducer


class AsyncKafkaProducer:
    def __init__(self, bootstrap_servers: str):
        self.bootstrap_servers = bootstrap_servers

    async def send_message(self, topic: str, key: str, value: dict):
        producer = AIOKafkaProducer(bootstrap_servers=self.bootstrap_servers)
        await producer.start()
        try:
            message = json.dumps(value).encode('utf-8')
            await producer.send_and_wait(
                topic=topic, key=key.encode('utf-8'), value=message
            )
        finally:
            await producer.stop()
