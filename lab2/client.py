# in client.py file
import queue
import socket
import subprocess
import threading
import time
from datetime import datetime, timezone

import grpc

import monitoring_app_pb2
import monitoring_app_pb2_grpc

INTERVAL = 10

metrics = {
    "memory_usage": "free | awk '/^Mem:/ { printf(\"%.2f\\n\", $3/$2 * 100) }'",
    "avg_cpu_usage": "top -bn1 | grep \"Cpu(s)\" | awk '{print 100 - $8}'",
    "read_io_stat": "iostat -d -k 1 1 | awk 'NR>7 {read+=$3} END {print read}'",
    "write_io_stat": "iostat -d -k 1 1 | awk 'NR>7 {write+=$4} END {print write}'",
}


def send_metrics(stub):
    for metric, cmd in metrics.items():
        try:
            out = subprocess.run(cmd, shell=True, capture_output=True, text=True).stdout
            value = float(out)
        except ValueError as e:
            print(f"{metric} ValueError:", e)
            continue
        try:
            stub.PeriodicReport(monitoring_app_pb2.MetricReport(
                time=datetime.now(timezone.utc).isoformat(),
                hostname=socket.gethostname(),
                metric=metric,
                value=value,
            ), timeout=2.0)
        except grpc.RpcError as e:
            pass


def run_command(text):

    r = subprocess.run(text, shell=True, capture_output=True, text=True, timeout=30)
    return r.stdout + r.stderr


def command_stream(stub):
    outgoing = queue.Queue()
    STOP = None

    def request_gen():

        while True:
            item = outgoing.get()
            if item is STOP:
                return
            yield item

    try:
        call = stub.CommandStream(request_gen())
        for cmd in call:
            print(f"Command: {cmd.message}")
            output = run_command(cmd.message)
            outgoing.put(monitoring_app_pb2.CommandResponse(command=output))
    except grpc.RpcError as e:
        print("Error:", e.code(), e.details())
    finally:
        outgoing.put(STOP)


def main():
    with grpc.insecure_channel("localhost:50051") as channel:
        stub = monitoring_app_pb2_grpc.MyServiceStub(channel)
        threading.Thread(target=command_stream, args=(stub,), daemon=True).start()
        while True:
            send_metrics(stub)
            time.sleep(INTERVAL)


if __name__ == "__main__":
    main()
