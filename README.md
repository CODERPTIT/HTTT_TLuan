# ABC Electronics E-Commerce Information System

ABC Electronics là ứng dụng thương mại điện tử mẫu dành cho đồ điện tử, được xây dựng bằng FastAPI, SQLAlchemy, SQLite, Jinja2 và JavaScript thuần. Dự án minh họa đầy đủ luồng khám phá sản phẩm, tìm kiếm đa phương thức, gợi ý sản phẩm, giỏ hàng, thanh toán mô phỏng, xử lý đơn hàng và theo dõi giao hàng theo vai trò.

> Đây là prototype phục vụ học tập và trình diễn. Hệ thống không thực hiện thanh toán thật, không kết nối trực tiếp với nhà cung cấp và không nên được triển khai công khai với dữ liệu cá nhân thực tế.

## Tính năng chính

- Duyệt danh mục và lọc sản phẩm trực tiếp từ catalog.
- Tìm kiếm bằng văn bản, hình ảnh, giọng nói hoặc kết hợp hình ảnh–văn bản.
- Trích xuất điều kiện tìm kiếm như danh mục, thương hiệu, màu sắc, khoảng giá và trạng thái còn hàng.
- Hiển thị thông tin chi tiết, thông số kỹ thuật và sản phẩm gợi ý.
- Đăng ký, đăng nhập, hồ sơ người dùng và phân quyền theo vai trò.
- Quản lý giỏ hàng, kiểm tra tồn kho và checkout có rollback khi thanh toán mô phỏng thất bại.
- Theo dõi đơn hàng qua năm trạng thái: `CONFIRMED`, `PROCESSING`, `SHIPPED`, `OUT_FOR_DELIVERY`, `DELIVERED`.
- Giao diện riêng cho Administrator, Sales Staff, Warehouse Staff, Manager và Shipping Provider.
- Lưu dữ liệu bằng SQLite và tự tạo dữ liệu mẫu trong lần chạy đầu tiên.
- Bộ kiểm thử tự động cho domain, service, repository, bảo mật, HTTP và kiến trúc.

## Công nghệ sử dụng

| Thành phần | Công nghệ |
| --- | --- |
| Backend | Python, FastAPI, Uvicorn |
| Persistence | SQLAlchemy, SQLite |
| Frontend | Jinja2, HTML, CSS, JavaScript |
| Text AI | OpenAI embeddings, structured output và reranking |
| Voice AI | OpenAI transcription |
| Image AI | SigLIP và OWL-ViT từ cache cục bộ; có fallback xử lý ảnh cơ bản |
| Testing | pytest, HTTPX và browser smoke test |

## Yêu cầu hệ thống

- Python 3.11 trở lên; dự án đã được kiểm tra với Python 3.14.
- Kết nối Internet và OpenAI API key nếu sử dụng tìm kiếm văn bản hoặc chép lời âm thanh.
- Node.js 22+ và Google Chrome chỉ cần cho browser smoke test.
- Model SigLIP/OWL-ViT đã có trong Hugging Face cache nếu muốn dùng xử lý ảnh nâng cao. Ứng dụng không tự tải model.

## Cài đặt và chạy

### Windows PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt

Copy-Item .env.example .env
.\.venv\Scripts\python.exe -m uvicorn main:app --host 127.0.0.1 --port 8000
```

Mở `http://127.0.0.1:8000` trên trình duyệt. Không cần activate virtual environment nên không phải thay đổi PowerShell Execution Policy.

### Linux hoặc macOS

```bash
python3 -m venv .venv
./.venv/bin/python -m pip install --upgrade pip
./.venv/bin/python -m pip install -r requirements.txt
cp .env.example .env
./.venv/bin/python -m uvicorn main:app --host 127.0.0.1 --port 8000
```

## Cấu hình môi trường

Ứng dụng tự đọc file `.env` tại thư mục gốc. Không commit file này lên Git.

```dotenv
OPENAI_API_KEY=
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
OPENAI_FILTER_MODEL=gpt-4o-mini
OPENAI_RERANK_MODEL=gpt-4o-mini
OPENAI_TRANSCRIPTION_MODEL=gpt-transcribe
AI_IMAGE_MODE=siglip
LOCAL_IMAGE_MODEL=Marqo/marqo-fashionSigLIP
AI_DETECT_MODE=owlvit
LOCAL_DETECTOR_MODEL=google/owlvit-base-patch32
```

Các biến tùy chọn khác:

| Biến | Mục đích |
| --- | --- |
| `ABC_RUNTIME` | Chọn thư mục chứa database, session secret và ảnh runtime. Mặc định là `runtime/`. |
| `ABC_HTTPS=1` | Bật cờ `Secure` cho session cookie khi chạy sau HTTPS. |
| `AI_IMAGE_MODE=basic` | Buộc sử dụng bộ đặc trưng màu/texture thay cho SigLIP. |
| `AI_DETECT_MODE=off` | Tắt phát hiện vùng vật thể bằng OWL-ViT. |

Nếu không có `OPENAI_API_KEY`, người dùng vẫn có thể duyệt danh mục, lọc category, xem sản phẩm, dùng giỏ hàng, checkout, recommendation và tìm kiếm ảnh bằng fallback cơ bản. Tìm kiếm văn bản bằng embedding và chép lời audio sẽ trả thông báo cấu hình rõ ràng.

## Dữ liệu khởi tạo

Lần chạy đầu tiên tự tạo:

- `runtime/electronics.db` chứa dữ liệu SQLite.
- `runtime/.session_secret` dùng để ký session cookie.
- Catalog gồm 24 sản phẩm thuộc 8 danh mục.
- Ba tài khoản Customer mẫu, bốn tài khoản nhân viên và một tài khoản Shipping Provider.
- Dữ liệu tương tác mẫu phục vụ recommendation.

Các lần chạy sau giữ nguyên dữ liệu hiện có. Có thể đặt `ABC_RUNTIME` sang một thư mục mới để tạo môi trường demo độc lập.

## Tài khoản demo

| Vai trò | Email | Mật khẩu | Quyền chính |
| --- | --- | --- | --- |
| Customer | `demo1@example.test` | `DemoCustomer123!` | Hồ sơ, giỏ hàng, checkout, đơn hàng và tracking |
| Customer | `demo2@example.test` | `DemoCustomer123!` | Tương tự Customer 1, có lịch sử tương tác riêng |
| Customer | `demo3@example.test` | `DemoCustomer123!` | Tương tự Customer 1, có lịch sử tương tác riêng |
| Administrator | `admin@abc.test` | `DemoStaff123!` | Cập nhật giá và trạng thái sản phẩm |
| Sales Staff | `sales@abc.test` | `DemoStaff123!` | Chuyển đơn từ confirmed sang processing |
| Warehouse Staff | `warehouse@abc.test` | `DemoStaff123!` | Cập nhật số lượng và chuyển đơn sang shipped |
| Manager | `manager@abc.test` | `DemoStaff123!` | Xem số liệu vận hành tổng hợp |
| Shipping Provider | `shipping@abc.test` | `DemoShipping123!` | Cập nhật shipment được giao sang out for delivery và delivered |

Customer sử dụng storefront; nhân viên truy cập `/staff`; Shipping Provider truy cập `/shipping`. Mật khẩu được băm bằng PBKDF2 trong database, nhưng các thông tin đăng nhập trên chỉ dành cho môi trường demo.

## Quy trình nghiệp vụ mẫu

1. Visitor duyệt catalog, category hoặc xem chi tiết sản phẩm.
2. Visitor/Customer tìm kiếm bằng text, image, voice hoặc image kết hợp text.
3. Customer đăng nhập, thêm sản phẩm vào giỏ và thay đổi số lượng.
4. Checkout kiểm tra quyền sở hữu, dữ liệu giao hàng và số lượng khả dụng.
5. Hệ thống tạo Order, OrderItem, Payment và Shipment trong cùng transaction.
6. Sales Staff chuyển đơn `CONFIRMED → PROCESSING`.
7. Warehouse Staff chuyển đơn và shipment sang `SHIPPED`.
8. Shipping Provider được gán chuyển shipment `SHIPPED → OUT_FOR_DELIVERY → DELIVERED`.
9. Khi giao COD thành công, payment pending được cập nhật thành paid.

## Kiểm thử

Chạy tại thư mục `abc-electronics`:

```powershell
.\.venv\Scripts\python.exe -m pytest -q --tb=short -p no:cacheprovider --basetemp "..\pytest-run-temp"
```

`--basetemp` đặt dữ liệu tạm trong vùng làm việc, tránh lỗi quyền truy cập thư mục `%TEMP%` trên Windows. Baseline hiện tại gồm 97 test tự động.

Browser smoke test yêu cầu Node.js 22+ và Google Chrome:

```powershell
$env:ABC_PYTHON = (Resolve-Path .\.venv\Scripts\python.exe).Path
node tests/browser_smoke.mjs
```

Browser test tự khởi động môi trường riêng, sử dụng các cổng 8765 và 9228, sau đó ghi kết quả vào `artifacts/`. Thư mục này là dữ liệu sinh tự động và không cần commit.

## Cấu trúc dự án

```text
abc-electronics/
├── application/          # Use-case services, search, recommendation và commerce
├── data/
│   ├── infrastructure/   # SQLite, image storage và vector index
│   └── repository/       # Repository implementations
├── domain/               # Entity, value object, enum và business invariant
├── presentation/
│   └── routes/           # HTTP routes theo nhóm chức năng
├── seeds/                # Catalog và dữ liệu demo
├── static/               # CSS, JavaScript và ảnh sản phẩm
├── templates/            # Giao diện Jinja2
├── tests/                # Automated tests và browser smoke test
├── bootstrap.py          # Composition root và dependency wiring
├── main.py               # FastAPI application factory
├── requirements.txt      # Python dependencies
└── .env.example          # Mẫu cấu hình, không chứa secret
```

Luồng phụ thuộc chính:

```text
Presentation → Application → Domain
                       ↓
              Repository Ports
                       ↑
Data / Infrastructure Implementations
```

`bootstrap.py` là composition root, chịu trách nhiệm tạo database, repository, application service và controller. Domain không phụ thuộc HTTP, SQLAlchemy hoặc repository cụ thể.

## Ghi chú về AI và recommendation

- Text search dùng OpenAI embedding để tạo shortlist, sau đó áp dụng structured filters và reranking.
- Image-only search dùng SigLIP khi model có sẵn trong cache; nếu không, hệ thống dùng đặc trưng màu/texture cơ bản.
- OWL-ViT chỉ phát hiện vùng vật thể khi model đã có trong cache cục bộ.
- Recommendation kết hợp 60% content-based và 40% item-based collaborative score.
- Khi chưa có đủ lịch sử tương tác, recommendation tự chuyển sang content-based cold start.
- Điểm tương đồng và điểm reranking chỉ dùng để sắp xếp trong prototype, không phải xác suất dự đoán tuyệt đối.

## Giới hạn của prototype

- Card và e-wallet chỉ được mô phỏng; không thu tiền thật.
- Shipping Provider cập nhật trạng thái thủ công, chưa tích hợp webhook/API vận chuyển.
- Chưa triển khai invoice, customer review, supplier replenishment, promotion engine hoặc return workflow.
- SQLite và xử lý đồng bộ phù hợp cho demo, chưa đại diện cho tải production.
- Chất lượng, độ trễ và chi phí của AI cần được đánh giá riêng với model trực tiếp và tập dữ liệu kiểm thử được kiểm soát.

## Bảo mật khi sử dụng

- Không commit `.env`, API key, database runtime hoặc session secret.
- Không sử dụng tài khoản demo khi triển khai công khai.
- Bật HTTPS và đặt `ABC_HTTPS=1` trước khi sử dụng ngoài localhost.
- Chỉ sử dụng dữ liệu và hình ảnh được phép chia sẻ.
