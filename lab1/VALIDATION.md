# Kết quả kiểm thử ngày 22/10/2026

Đã chạy thực tế trên workspace này bằng Docker 29.9.1, k3d 5.8.3, k3s 1.34.1 và kubectl 1.34.1.

| Phép kiểm tra | Kết quả |
| --- | --- |
| Script 00 | Binary k3d/kubectl khớp checksum phát hành chính thức |
| Script 01 | Hai node Ready, CoreDNS và local-path provisioner hoạt động |
| Script 02 | Hai pod Nginx trên hai node; HTTP localhost:8080 trả trang Welcome to nginx |
| Script 03 | Hai broker Ready, hai PVC Bound; topic có 3 partition, RF 2 và ISR đủ 2 broker |
| Script 04 | Producer giao đủ 10 message; consumer đọc được dữ liệu; smoke test PASS trên cả ba partition |
| Restart kafka-0 | Pod được tạo lại với PVC cũ; consumer group mới đọc lại đủ 10 message đã gửi trước restart |
| Hai consumer cùng group | Group `lab1-group-validation`: một consumer nhận partition 2; consumer còn lại nhận partition 0 và 1; log xác nhận cả hai nhận message |
| Script 05 | Đã lưu trạng thái cluster, HTTP, topic và kết quả smoke test vào thư mục evidence |
| Kafka UI (script 06–07) | Kafbat UI 1.5.0 Ready; localhost:8081 trả HTTP 200; API báo cluster ds-lab1 ONLINE, 2 broker, thấy lab1-demo có 3 partition/RF 2 và không có partition thiếu replica |
| Kiểm tra tĩnh | Tất cả script qua bash -n; Python qua kiểm tra cú pháp; manifest qua schema k3d và OpenAPI Kubernetes 1.34.1; git diff --check không báo lỗi |

Minh chứng của lượt chạy này ở `evidence/20261022-082401/` (file cục bộ, được gitignore). Có thể chạy lại script 05 để thu bộ minh chứng mới. Cluster `ds-lab1` được giữ chạy để tiếp tục thực hành; công cụ và kubeconfig nằm riêng trong `lab1/`.

Đây là kết quả thử nghiệm, không thay cho báo cáo nhóm và video cần nộp. Chưa kiểm tra khả năng chịu lỗi mất node vật lý; hai node k3d cùng nằm trên một host, và quorum hai controller không chịu được mất một controller.
