"""Verify ten unique messages across all three partitions, ignoring older runs."""
import time
import uuid

from confluent_kafka import Consumer, KafkaException
from producer import BOOTSTRAP, send_messages


def main():
    run_id = f"smoke-{uuid.uuid4().hex}"
    expected = {f"{run_id} {i}" for i in range(10)}
    send_messages(BOOTSTRAP, "lab1-demo", prefix=run_id)
    consumer = Consumer({"bootstrap.servers": BOOTSTRAP, "group.id": run_id,
                         "auto.offset.reset": "earliest", "enable.auto.commit": False})
    received, partitions = set(), set()
    deadline = time.monotonic() + 60
    try:
        consumer.subscribe(["lab1-demo"])
        while received != expected and time.monotonic() < deadline:
            message = consumer.poll(1)
            if message is None:
                continue
            if message.error():
                raise KafkaException(message.error())
            value = message.value().decode() if message.value() is not None else ""
            if value in expected:
                received.add(value)
                partitions.add(message.partition())
        if received != expected or partitions != {0, 1, 2}:
            raise RuntimeError(f"Missing={expected - received}; partitions={partitions}")
        print("PASS: received all 10 unique messages across partitions 0, 1, 2")
    finally:
        consumer.close()


if __name__ == "__main__":
    main()
