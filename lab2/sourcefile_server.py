# in server.py file
import time
import grpc

import monitoring_app_pb2
import monitoring_app_pb2_grpc

from concurrent import futures

class GreeterServicer(monitoring_app_pb2_grpc.GreeterServicer):
    def SayHello(self, request, context):
        # Unary: return one response
        msg = f"Hello, {request.name}!"
        return monitoring_app_pb2.HelloReply(message=msg)

    def LotsOfReplies(self, request, context):
        # Server streaming: yield multiple messages
        name = request.name or "friend"
        for i in range(5):
            yield monitoring_app_pb2.HelloReply(message=f"[{i}] Hi {name} from stream")
            time.sleep(0.3) # for demo pacing

def serve():
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10)) # set the number of threads server are using
        monitoring_app_pb2_grpc.add_GreeterServicer_to_server(GreeterServicer(), server)
        server.add_insecure_port("[::]:50051") # listen on all interfaces in port 50051
        server.start()
        print("gRPC server running on :50051")
        try:
            server.wait_for_termination()
        except KeyboardInterrupt:
            print("Shutting down...")


if __name__ == "__main__":
    serve()
