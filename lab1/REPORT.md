# Báo cáo Lab 1 — Distributed System

> Điền kết quả quan sát thật sau khi chạy lab. Đây là mẫu báo cáo, chưa phải minh chứng triển khai thành công.

## 1. Thành viên và môi trường

- Thành viên/MSSV: ...
- OS, Docker, CPU/RAM: ...
- Phiên bản k3d, k3s, kubectl, Kafka, Python: ...
- Dùng k3d/k3s theo sự cho phép của người hướng dẫn, thay cho hai VM kubeadm.

## 2. Kiến trúc

Mô tả host → hai node k3d → Flannel/CoreDNS/local-path → Nginx và Kafka. Kafka gồm hai broker/controller KRaft, headless DNS, StatefulSet và hai PVC. Python client chạy trong cluster. Phân biệt hai node container với hai máy vật lý.

## 3. Các bước và kết quả

| Bước | Minh chứng cần ghi | Kết quả thực tế |
| --- | --- | --- |
| Kubernetes | Hai node Ready, system pods Running | ... |
| Nginx | Hai pod trên hai node, NodePort và ảnh trang 8080 | ... |
| Kafka | Hai pod Ready, PVC Bound, topic 3 partition/RF 2/ISR 2 | ... |
| Python | Delivery callback, topic/partition/offset, smoke PASS | ... |
| Consumer group | Partition chia cho hai consumer cùng group | ... |
| Persistence | Restart một pod, đọc lại message trước đó | ... |

## 4. Giải thích và hạn chế

- Vì sao cần StatefulSet/headless Service/PVC?
- Partition, replication factor, ISR và consumer group khác nhau như thế nào?
- Vì sao hai controller không chịu được lỗi một controller?
- Những điểm khác với PDF và lý do (k3d/k3s, Kafka version, DNS client, startup/format).
- Local-path giữ dữ liệu qua pod restart nhưng có giới hạn khi mất node/cluster.

## 5. Video demo

- Link video: ...
- Trình tự: node/pod → Nginx trên trình duyệt → Kafka/PVC/topic → producer/consumer → hai consumer cùng group → restart pod và đọc lại dữ liệu.

## 6. Kết luận

Ghi phần đã kiểm chứng, lỗi gặp và cách xử lý; không ghi thành công cho phép thử chưa chạy.
