# in client.py file
import grpc
import monitoring_app_pb2
import monitoring_app_pb2_grpc

import subprocess
command = "ps aux"
result = subprocess.run(command, shell=True, capture_output=True, text=True)
print(result.stdout)

def unary_example(stub):
    try:
        resp = stub.SayHello(monitoring_app_pb2.HelloRequest(name="Binh"), timeout=2.0)
        print("Unary response:", resp.message)
    except grpc.RpcError as e:
        print("Unary failed:", e.code(), e.details())

def server_streaming_example(stub):
    try:
        stream = stub.LotsOfReplies(monitoring_app_pb2.HelloRequest(name="Binh"), timeout=3.0)
        for msg in stream:
            print("Stream item:", msg.message)
    except grpc.RpcError as e:
            print("Stream failed:", e.code(), e.details())
def main():
    with grpc.insecure_channel("localhost:50051") as channel:
        stub = monitoring_app_pb2_grpc.GreeterStub(channel)
        print(111)
        unary_example(stub)
        server_streaming_example(stub)


if __name__ == "__main__":
    main()
