# utils/kafka_helper.py
from kafka import KafkaProducer, KafkaConsumer
import json
from config import KAFKA_BOOTSTRAP

def get_producer():
    return KafkaProducer(
        bootstrap_servers=KAFKA_BOOTSTRAP,
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        retries=5
    )

def get_consumer(topics, group_id):
    return KafkaConsumer(
        *topics,
        bootstrap_servers=KAFKA_BOOTSTRAP,
        auto_offset_reset='latest',
        enable_auto_commit=True,
        value_deserializer=lambda x: json.loads(x.decode("utf-8")),
        group_id=group_id
    )
