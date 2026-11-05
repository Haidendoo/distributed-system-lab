## Installation
  Cần uv để quản lý môi trường. Khởi tạo và install dependancies:

  
```bash
  uv venv --python 3.10 .venv
  source .venv/bin/activate
  uv pip install "protobuf==3.20.3" "grpcio==1.48.2" "grpcio-tools==1.48.2"
```

## Development:
  1. Define grpc interface and msg structure in *.proto
  2. Compile file đó dùng lệnh
```python
python3 -m grpc_tools.protoc -I . --python_out=. --grpc_python_out=. monitoring_app.proto
```
  3. 2 file mới được sinh ra là *_pb2.py (định nghĩa message type) và *_pb2_gprc.py (định nghĩa grpc server ở phía server và grpc stub ở phía client)
  4. implement 2 file server.py và client.py, sử dụng grpc server và grpc stub

## Demo:
  1. Bật 2 terminal khác nhau, chạy lần lượt 2 lệnh sau.
#### Task 1: Implement multiple client applications (corresponding to the number of group
members) that periodically send monitoring data to the server.
##### Terminal 1
```uv
uv run server.py
```
##### Terminal 2 - n
```uv
uv run client.py
````
Client âm thầm chạy các lệnh và gửi về server=)) 





