"""Send the ten messages from the lab, checking every delivery result."""
import argparse
import os
import sys

from confluent_kafka import Producer

BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka-service.kafka.svc.cluster.local:9092")


def send_messages(bootstrap, topic, count=10, prefix="Hello Kafka"):
    producer = Producer({"bootstrap.servers": bootstrap, "acks": "all",
                         "enable.idempotence": True, "message.timeout.ms": 30000})
    errors = []

    def delivered(error, message):
        if error:
            errors.append(str(error))
        else:
            print(f"Delivered: {message.topic()} [{message.partition()}] "
                  f"offset={message.offset()}", flush=True)

    for i in range(count):
        # Explicit partitions make the consumer-group demo reproducible.
        producer.produce(topic, value=f"{prefix} {i}".encode(), partition=i % 3,
                         callback=delivered)
        producer.poll(0)
    pending = producer.flush(40)
    if errors or pending:
        raise RuntimeError(f"Delivery errors={errors}; pending={pending}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bootstrap", default=BOOTSTRAP)
    parser.add_argument("--topic", default="lab1-demo")
    parser.add_argument("--count", type=int, default=10)
    args = parser.parse_args()
    if args.count < 1:
        parser.error("--count must be positive")
    try:
        send_messages(args.bootstrap, args.topic, args.count)
    except Exception as error:
        print(error, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
