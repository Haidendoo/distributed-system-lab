# in server.py file
import queue
import threading
from concurrent import futures

import grpc

import monitoring_app_pb2
import monitoring_app_pb2_grpc


class MyServiceServicer(monitoring_app_pb2_grpc.MyServiceServicer):
    def __init__(self):
        self.lock = threading.Lock()
        self.outgoing = None   

    def send_command(self, text):
        with self.lock:
            if self.outgoing is None:
                print("Disconnected")
                return
            self.outgoing.put(monitoring_app_pb2.CommandRequest(message=text))

    def PeriodicReport(self, request, context):
        print(f"({request.time}, {request.hostname}, {request.metric}, {request.value})")
        return monitoring_app_pb2.CommandRequest(message="Received")

    def CommandStream(self, request_iterator, context):
        q = queue.Queue()
        with self.lock:
            self.outgoing = q

        def reader():
            try:
                for resp in request_iterator:
                    print(f"[client result]\n{resp.command}")
            except grpc.RpcError:
                pass
            finally:
                q.put(None)   
                
        threading.Thread(target=reader, daemon=True).start()
        try:
            while True:
                cmd = q.get()
                if cmd is None:
                    break
                yield cmd
        finally:
            with self.lock:
                if self.outgoing is q:
                    self.outgoing = None


def cli(servicer):
    while True:
        line = input("> ").strip()
        if line == "quit":
            return
        if line:
            servicer.send_command(line)


def serve():
    servicer = MyServiceServicer()
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    monitoring_app_pb2_grpc.add_MyServiceServicer_to_server(servicer, server)
    server.add_insecure_port("[::]:50051")
    server.start()
    print("gRPC server running on :50051")
    try:
        cli(servicer)
    finally:
        server.stop(0)


if __name__ == "__main__":
    serve()
