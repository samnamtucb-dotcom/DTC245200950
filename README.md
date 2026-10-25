# Restaurant Management System

**MSSV:** DTC245200950  
**Đề tài:** Hệ thống Quản lý Nhà hàng  
**Môn học:** Triển khai và Quản trị Hệ thống Phần mềm

## 1. Giới thiệu

Đây là hệ thống quản lý nhà hàng được xây dựng và triển khai bằng Docker Compose. Dự án tập trung vào quá trình triển khai, quản trị, giám sát, thu thập log tập trung và tăng cường bảo mật cho hệ thống.

## 2. Công nghệ sử dụng

- FastAPI / Python
- PostgreSQL
- pgAdmin
- Nginx
- Docker / Docker Compose
- Prometheus
- PostgreSQL Exporter
- Grafana
- Loki
- Promtail

## 3. Kiến trúc hệ thống

Hệ thống gồm các service chính:

| Service | Chức năng |
|---|---|
| app | Web application FastAPI |
| db | Cơ sở dữ liệu PostgreSQL |
| pgadmin | Công cụ quản trị PostgreSQL |
| nginx | Reverse Proxy |
| prometheus | Thu thập metrics |
| postgres-exporter | Xuất metrics PostgreSQL cho Prometheus |
| grafana | Trực quan hóa và giám sát |
| loki | Lưu trữ log tập trung |
| promtail | Thu thập log từ Docker containers |

Luồng truy cập chính:

```text
Client
  |
  v
Nginx
  |
  v
FastAPI
  |
  v
PostgreSQL
```

Hệ thống monitoring:

```text
FastAPI ----------\
                   \
Postgres Exporter ---> Prometheus ---> Grafana
```

Hệ thống logging:

```text
Docker Containers ---> Promtail ---> Loki ---> Grafana
```

## 4. Cấu hình môi trường

Tạo file `.env` dựa trên `.env.example`.

Ví dụ:

```env
POSTGRES_DB=restaurant_db
POSTGRES_USER=restaurant_admin
POSTGRES_PASSWORD=your_strong_password

PGADMIN_DEFAULT_EMAIL=admin@example.com
PGADMIN_DEFAULT_PASSWORD=your_strong_password

GRAFANA_ADMIN_PASSWORD=your_strong_password
```

Không commit file `.env` chứa thông tin bí mật lên GitHub.

## 5. Khởi chạy hệ thống

Yêu cầu:

- Docker Desktop
- Docker Compose

Khởi chạy toàn bộ hệ thống:

```bash
docker compose up -d --build
```

Kiểm tra trạng thái:

```bash
docker compose ps
```

Dừng hệ thống:

```bash
docker compose down
```

## 6. Truy cập các dịch vụ

Sau khi khởi chạy thành công:

| Thành phần | Địa chỉ |
|---|---|
| Website qua Nginx | `http://localhost` |
| FastAPI trực tiếp | `http://localhost:8000` |
| pgAdmin | `http://localhost:5050` |
| Grafana | `http://localhost:3000` |
| Prometheus | `http://localhost:9090` |

## 7. Monitoring

FastAPI cung cấp endpoint metrics để Prometheus thu thập.

Ví dụ PromQL:

```promql
up
```

Kiểm tra trạng thái FastAPI:

```promql
up{job="restaurant-app"}
```

Theo dõi tổng HTTP request:

```promql
sum(http_requests_total)
```

PostgreSQL được giám sát thông qua `postgres-exporter`.

Metrics được trực quan hóa trên Grafana.

## 8. Centralized Logging

Promtail thu thập log từ Docker containers và gửi về Loki.

Có thể truy vấn log trong Grafana Explore bằng LogQL.

Ví dụ:

```logql
{container="restaurant-nginx"}
```

Lọc các request tới health endpoint:

```logql
{container="restaurant-nginx"} |= "/health"
```

Lọc HTTP request thành công:

```logql
{container="restaurant-nginx"} |= "200"
```

## 9. Security / Hardening

Một số biện pháp hardening được áp dụng:

- FastAPI container chạy bằng non-root user `appuser`.
- PostgreSQL không publish trực tiếp cổng 5432 ra host.
- Database được đặt trong Docker backend network.
- Backend network được cấu hình `internal: true`.
- Sử dụng biến môi trường cho tài khoản và mật khẩu.
- File `.env` được loại khỏi Git bằng `.gitignore`.
- Nginx được sử dụng làm reverse proxy.
- Nginx bổ sung các HTTP security headers.
- Các file cấu hình được mount read-only khi phù hợp.
- Healthcheck được sử dụng để kiểm tra trạng thái ứng dụng và database.

Kiểm tra user bên trong FastAPI container:

```bash
docker compose exec app whoami
```

Kết quả mong đợi:

```text
appuser
```

## 10. Cấu trúc thư mục

```text
restaurant-management/
├── app/
├── loki/
│   └── loki-config.yml
├── nginx/
│   └── nginx.conf
├── prometheus/
│   └── prometheus.yml
├── promtail/
│   └── promtail-config.yml
├── .dockerignore
├── .env.example
├── .gitignore
├── compose.yml
├── Dockerfile
├── requirements.txt
└── README.md
```

## 11. Kiểm tra nhanh

Kiểm tra toàn bộ container:

```bash
docker compose ps
```

Kiểm tra FastAPI:

```text
http://localhost/health
```

Kiểm tra Prometheus targets bằng truy vấn:

```promql
up
```

Kiểm tra log Nginx trong Grafana/Loki:

```logql
{container="restaurant-nginx"} |= "/health"
```

## 12. Repository

Repository được quản lý bằng Git và GitHub theo MSSV:

`DTC245200950`