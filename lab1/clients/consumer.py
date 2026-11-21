"""Consume messages; optionally stop after a count or a bounded timeout."""
import argparse
import sys
import time

from confluent_kafka import Consumer, KafkaException
from producer import BOOTSTRAP


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bootstrap", default=BOOTSTRAP)
    parser.add_argument("--topic", default="lab1-demo")
    parser.add_argument("--group", default="test-group")
    parser.add_argument("--offset", choices=["earliest", "latest"], default="earliest")
    parser.add_argument("--count", type=int, default=0, help="0: keep listening")
    parser.add_argument("--timeout", type=float, default=0, help="0: no deadline")
    args = parser.parse_args()
    if args.count < 0 or args.timeout < 0:
        parser.error("count and timeout cannot be negative")
    consumer = Consumer({"bootstrap.servers": args.bootstrap, "group.id": args.group,
                         "auto.offset.reset": args.offset, "enable.auto.commit": False})
    received = 0
    started = time.monotonic()
    try:
        consumer.subscribe([args.topic])
        while not args.count or received < args.count:
            if args.timeout and time.monotonic() - started >= args.timeout:
                if args.count and received < args.count:
                    raise TimeoutError(f"Received {received}/{args.count} messages")
                break
            message = consumer.poll(1.0)
            if message is None:
                continue
            if message.error():
                raise KafkaException(message.error())
            value = message.value()
            print(f"Received: {value.decode('utf-8') if value is not None else '<null>'} "
                  f"from {message.topic()} [{message.partition()}] "
                  f"offset={message.offset()}", flush=True)
            consumer.commit(message=message, asynchronous=False)
            received += 1
    except KeyboardInterrupt:
        print("Stopping consumer")
    except Exception as error:
        print(error, file=sys.stderr)
        return 1
    finally:
        consumer.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
