# Lab 1 — Kubernetes và Apache Kafka bằng k3d

Triển khai tuần tự theo `Distributed_System__Lab_1.pdf`. Theo lựa chọn được người hướng dẫn cho phép, dùng **k3d/k3s** thay cho kubeadm trên hai VM Ubuntu. Các phần workload vẫn gồm Nginx hai replica, Kafka hai broker KRaft, topic và producer/consumer Python.

Đã chạy kiểm thử thực tế trong workspace; xem [VALIDATION.md](VALIDATION.md) để biết kết quả và giới hạn của phép thử.

## 0. Chuẩn bị

Chạy trong Linux hoặc WSL2 có Docker Engine/Docker Desktop đang hoạt động. Cần `bash`, `curl`, `sha256sum`, `python3`, quyền truy cập Docker và Internet để tải công cụ/image/thư viện. Nên dành khoảng 4 CPU, 6 GiB RAM và 25 GiB dung lượng trống cho lab.

Chạy tất cả lệnh dưới đây **từ thư mục gốc repo**, lần lượt từng bước. Script dừng khi một lệnh lỗi; xử lý lỗi rồi mới sang bước tiếp theo.

```bash
docker info
bash lab1/scripts/00-install-tools.sh
```

Công cụ được tải vào `lab1/.bin`, có kiểm tra SHA-256, không cài vào `/usr/local/bin`. Phiên bản được ghim: k3d 5.8.3, k3s/Kubernetes 1.34.1, kubectl 1.34.1, Kafka 3.9.1 và Python 3.10.18.

## 1. Tạo Kubernetes cluster — thay phần 1.1 và 1.2 của PDF

```bash
bash lab1/scripts/01-create-cluster.sh
```

Cluster tên `ds-lab1` có một server (control plane, đồng thời chạy workload) và một agent (worker), là hai container Docker trên cùng máy. Đây là hai node Kubernetes nhưng không phải hai máy vật lý độc lập.

k3s cung cấp sẵn Flannel CNI, CoreDNS và local-path provisioner. Vì vậy không cài thêm Calico hoặc provisioner Rancher lần nữa. Tắt Traefik và ServiceLB để tập trung vào NodePort như đề bài. Không tạo thêm container load balancer của k3d vì chỉ có một server; API map trực tiếp vào server. Không cần tắt swap/firewall hoặc thay cấu hình containerd của máy host.

Kỳ vọng: hai node `Ready`, CoreDNS và local-path provisioner `Running`, StorageClass `local-path` tồn tại. Bước 01 có thể chạy lại để dùng cluster hiện có; không tự xóa dữ liệu.

Để chạy `kubectl` thủ công ở terminal hiện tại:

```bash
export PATH="$PWD/lab1/.bin:$PATH"
export KUBECONFIG="$PWD/lab1/.kubeconfig"
kubectl get nodes -o wide
kubectl get pods -A
```

Các script tự đặt kubeconfig riêng này; không đổi context mặc định của người dùng. API cluster chỉ bind `127.0.0.1:6550`.

## 2. Kiểm tra Kubernetes bằng Nginx — phần 1.3

```bash
bash lab1/scripts/02-deploy-nginx.sh
```

Mở <http://localhost:8080>, kỳ vọng trang **Welcome to nginx!**. NodePort `30080` được k3d map sang cổng `8080` của host. Deployment ở namespace `lab1`, gồm hai pod; required pod anti-affinity buộc mỗi pod chạy trên một node khác nhau (chỉ đặt `replicas: 2` không bảo đảm điều này).

```bash
kubectl -n lab1 get pods -o wide
kubectl -n lab1 get svc web-app
```

## 3. Triển khai Kafka — phần 2.2

```bash
bash lab1/scripts/03-deploy-kafka.sh
```

Manifest có namespace `kafka`, ConfigMap cấu hình, headless Service và StatefulSet hai replica. Mỗi broker đồng thời là controller, có PVC 10 GiB riêng và chạy trên một node riêng. Local-path cấp thư mục trên node khi cần, không đặt trước quota đĩa cứng 10 GiB.

Topic `lab1-demo` có **3 partition**, **replication factor 2**. `--describe` phải hiển thị hai broker trong `Replicas` và `Isr` cho từng partition. Internal topic của consumer group cũng được cấu hình replication factor 2, phù hợp cluster chỉ có hai broker.

```bash
kubectl -n kafka get pods,pvc -o wide
kubectl -n kafka logs kafka-0 --tail=50
kubectl -n kafka exec kafka-0 -- /opt/kafka/bin/kafka-topics.sh \
  --bootstrap-server kafka-service:9092 --describe --topic lab1-demo
```

Các sửa đổi so với mẫu PDF:

- Ghim Kafka 3.9.1 thay cho `latest`, dùng static KRaft quorum (`controller.quorum.voters`) nhất quán.
- Tạo file cấu hình mới mỗi lần khởi động, không nối lặp vào file có sẵn. `--ignore-formatted` cho phép dùng lại volume đã format khi pod restart; cluster ID giữ nguyên.
- Chỉ quảng bá listener broker cho client; controller listener dành cho quorum.
- `publishNotReadyAddresses: true` và tạo pod song song giúp hai controller tìm thấy nhau trong quá trình bootstrap.
- Đặt quyền volume cho UID/GID 1000, thêm readiness/startup probe.

Hai controller cần cả hai để đạt đa số. Cluster này phục vụ bài lab, **không chịu được mất một controller**; cấu hình `acks=all`, `min.insync.replicas=2` cũng dừng ghi khi thiếu một replica. Muốn ba controller cần một thiết kế quorum/migration riêng, không chỉ tăng `replicas` của static quorum đang chạy.

## 4. Chạy producer và consumer Python

```bash
bash lab1/scripts/04-test-python.sh
```

Script tạo ConfigMap mã Python, chạy pod client Python 3.10, cài `confluent-kafka==2.8.2`, rồi:

1. Producer gửi `Hello Kafka 0` đến `Hello Kafka 9`, kiểm tra callback và flush.
2. Consumer dùng group mới, đọc 10 message và in topic/partition/offset. Nếu topic đã có dữ liệu, đây có thể là message từ lần chạy trước.
3. Smoke test gửi 10 message với ID riêng cho lần chạy, kiểm tra đủ 10 giá trị trên cả ba partition. Kỳ vọng dòng `PASS: received all 10 unique messages across partitions 0, 1, 2`.

Client chạy trong cluster để phân giải DNS của **mọi broker** mà Kafka quảng bá. Không cần sửa `/etc/hosts`. Chỉ `port-forward` một broker chưa đủ cho client trên host vì metadata Kafka trả về địa chỉ của các broker khác.

Chạy riêng từng chương trình:

```bash
# Terminal 1: nghe liên tục, Ctrl+C để dừng
kubectl -n kafka exec -it deployment/kafka-client -- \
  python consumer.py --group test-group

# Terminal 2: gửi 10 message
kubectl -n kafka exec deployment/kafka-client -- python producer.py
```

`earliest` chỉ áp dụng khi group chưa có offset đã commit. Dùng `--group ten-moi` để đọc từ đầu; `--offset latest` để bắt đầu từ message mới khi group chưa có offset. Chờ consumer được gán partition trước khi gửi nếu dùng `latest`.

Demo consumer group: mở hai terminal chạy cùng `--group parallel-demo --offset latest`, đợi ổn định rồi chạy producer. Ba partition sẽ được chia giữa hai consumer; mỗi partition chỉ có một consumer trong group đọc tại một thời điểm. Hai group khác nhau đều nhận được toàn bộ luồng. Producer phân phối tường minh qua ba partition để dễ quan sát.

## 5. Kiểm tra lưu trữ sau khi pod restart

Sau khi bước 04 đã PASS:

```bash
kubectl -n kafka delete pod kafka-0
kubectl -n kafka wait --for=create pod/kafka-0 --timeout=60s
kubectl -n kafka wait --for=condition=Ready pod/kafka-0 --timeout=300s
kubectl -n kafka rollout status statefulset/kafka --timeout=300s
kubectl -n kafka exec deployment/kafka-client -- \
  python consumer.py --group persistence-check-1 --count 10 --timeout 60
```

Đổi tên group nếu lặp lại phép thử. Kỳ vọng pod được tạo lại, dùng PVC cũ và consumer vẫn đọc được message đã lưu. Trong thời gian controller restart, cluster có thể tạm ngừng xử lý. Restart pod khác với xóa node/cluster: local-path gắn dữ liệu với node, không tự sao chép volume giữa hai node.

## 6. Báo cáo và video — phần 3

```bash
bash lab1/scripts/05-collect-evidence.sh
```

Kết quả lưu ở `lab1/evidence/<thoi-gian>/` (đã gitignore). Script chạy lại smoke test thật; không tạo kết quả giả. Ghi báo cáo theo [REPORT.md](REPORT.md), kèm ảnh trình duyệt và video demo. Đề không có thêm bài lập trình riêng ở phần 3; yêu cầu nộp báo cáo và video triển khai.

## 7. Kafka UI trên trình duyệt

Dùng [Kafbat Kafka UI](https://github.com/kafbat/kafka-ui), image ghim phiên bản 1.5.0, chạy trong namespace `kafka` và kết nối hai broker qua DNS nội bộ.

```bash
bash lab1/scripts/06-deploy-kafka-ui.sh
bash lab1/scripts/07-forward-kafka-ui.sh
```

Giữ terminal forwarding đang chạy và mở <http://localhost:8081>. Chọn cluster `ds-lab1` để xem brokers, topic `lab1-demo`, partitions, messages và consumer groups. UI cũng cho phép thao tác tạo topic/gửi message trong lab.

Luồng truy cập: `localhost:8081 → kubectl port-forward → service/kafka-ui:8080 → pod Kafka UI`. Cổng chỉ bind localhost, không cần thay cấu hình hay tạo lại cluster k3d. Nginx tiếp tục dùng cổng 8080.

Nếu đã thiết lập PATH/KUBECONFIG, có thể forward thủ công:

```bash
kubectl -n kafka port-forward --address 127.0.0.1 svc/kafka-ui 8081:8080
```

`Ctrl+C` dừng forwarding, pod UI vẫn chạy. Khi stop/start cluster hoặc pod UI bị thay thế, chạy lại script 07. Nếu cổng 8081 bị dùng, có thể forward thủ công với `8082:8080` rồi mở cổng 8082.

Nếu forwarding đã được khởi chạy nền trong workspace này, PID và log nằm ở `lab1/.runtime/kafka-ui-port-forward.pid` và `lab1/.runtime/kafka-ui-port-forward.log`. Dừng tiến trình nền trước khi chạy script 07 trong terminal khác:

```bash
kill "$(cat lab1/.runtime/kafka-ui-port-forward.pid)"
```

## Xử lý lỗi

| Triệu chứng | Kiểm tra / xử lý |
| --- | --- |
| Docker permission denied | Kiểm tra Docker Desktop/Engine và quyền Docker của tài khoản. Chạy trong terminal có quyền Docker. |
| Cổng 6550 hoặc 8080 bị dùng | Đổi hostPort/port trong `k3d.yaml` trước khi tạo; nếu đổi 8080, sửa URL trong script 02 và 05 tương ứng. |
| Pod Pending | `kubectl -n kafka describe pod kafka-0`, kiểm tra hai node Ready, CPU/RAM và PVC. Anti-affinity cần đủ hai node. |
| PVC Pending | `kubectl get sc`; `kubectl -n kube-system logs deployment/local-path-provisioner`. |
| ImagePullBackOff | `kubectl describe pod ...`, kiểm tra Internet/DNS/Docker Hub và dung lượng đĩa. |
| Client không Ready | `kubectl -n kafka logs deployment/kafka-client`; pod cần truy cập PyPI để cài thư viện. |
| Kafka CrashLoopBackOff | `kubectl -n kafka logs kafka-0 --previous`; kiểm tra quyền PVC, quorum và cluster ID. |
| Consumer không có message | Group cũ có thể đã commit offset; đổi group. Kiểm tra topic, ISR, log producer. |

## Dừng hoặc xóa lab

```bash
# Dừng để giữ lại cluster và dữ liệu
lab1/.bin/k3d cluster stop ds-lab1
# Khởi động lại, sau đó chạy bước 01 để cập nhật kubeconfig/kiểm tra
lab1/.bin/k3d cluster start ds-lab1
```

**Chỉ chạy các lệnh dưới đây khi muốn xóa lab và dữ liệu Kafka:**

```bash
lab1/.bin/k3d cluster delete ds-lab1
rm -f lab1/.kubeconfig
```

Không chạy các lệnh reset kubeadm/xóa `/etc/kubernetes` trong PDF trên máy host dùng k3d.

## Tài liệu tham khảo

- Đề bài: [Distributed_System__Lab_1.pdf](Distributed_System__Lab_1.pdf).
- [k3d config file](https://k3d.io/v5.7.3/usage/configfile/).
- [K3s networking](https://docs.k3s.io/networking) và [storage](https://docs.k3s.io/storage).
- [Apache Kafka KRaft](https://kafka.apache.org/39/operations/kraft/) và [Docker image](https://kafka.apache.org/39/getting-started/docker/).
