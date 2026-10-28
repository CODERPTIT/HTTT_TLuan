# ABC Electronics — Chapter 4.5

Ứng dụng thương mại điện tử mẫu dùng Python, FastAPI, SQLAlchemy, SQLite, Jinja2 và JavaScript thuần. Kiến trúc bốn lớp giữ các package/class trong tài liệu `CODEX_CHAPTER_4_5_ABC_ELECTRONICS.md`.

## Chạy trên Windows PowerShell

Yêu cầu Python 3.11 trở lên. Các phiên bản dependency đã được kiểm tra với Python 3.14.

```powershell
cd D:\HTTT_TieuLuan\abc-electronics
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn main:app --host 127.0.0.1 --port 8000
```

Mở http://127.0.0.1:8000. Không cần activate môi trường, do đó không cần thay đổi ExecutionPolicy của PowerShell.

Nếu Python hiện tại đã có các dependency:

```powershell
cd D:\HTTT_TieuLuan\abc-electronics
python -m uvicorn main:app --host 127.0.0.1 --port 8000
```

Khởi động lần đầu tự tạo `runtime/electronics.db` và ảnh minh họa cục bộ. Seed gồm 24 sản phẩm, 8 danh mục, 10 thương hiệu, 3 khách hàng mẫu và lịch sử tương tác. Chạy lại không ghi đè dữ liệu đã mua. Có thể đặt `ABC_RUNTIME` sang thư mục mới để có bộ dữ liệu demo độc lập.

## Kiểm thử

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

Kiểm thử gồm domain, tìm kiếm text/voice/image, giỏ hàng, checkout, rollback, snapshot giá, recommendation, order, HTTP routes, upload, HTML escaping và kiểm tra dependency bằng AST.

Kiểm tra trình duyệt thực, cần Node.js 22+ và Google Chrome:

```powershell
$env:ABC_PYTHON = (Resolve-Path .\.venv\Scripts\python.exe).Path
node tests/browser_smoke.mjs
```

Script chạy trên cổng 8765 và 9228, tự dừng các tiến trình do nó tạo, xuất ảnh và JSON vào `artifacts/`. Không dùng dữ liệu demo đang chạy của bạn.

## Kịch bản demo

1. Trang chủ: danh mục, featured, deals, recommendation.
2. Tìm `gaming laptop`, `Samsung 4K TV`, `wireless noise cancelling headphones`, `phone under 20 million`.
3. Chọn biểu tượng voice, sử dụng microphone nếu trình duyệt hỗ trợ, hoặc nhập transcript mẫu. Browser speech có thể cần dịch vụ của trình duyệt; transcript fallback chạy hoàn toàn offline.
4. Chọn biểu tượng image, tải JPG/PNG/WebP tối đa 5 MB. Có thể dùng `runtime/images/product-4.png` làm mẫu. Bộ so khớp local sử dụng màu và texture, không nhận diện ngữ nghĩa như CLIP.
5. Mở chi tiết sản phẩm để xem specifications và recommendation; lượt xem tạo Interaction VIEW.
6. Thêm sản phẩm vào giỏ, đổi số lượng, xóa sản phẩm.
7. Checkout bằng COD, simulated card hoặc e-wallet. Không nhập số thẻ thật.
8. Chọn “Simulate card / e-wallet failure” để kiểm tra rollback: giỏ và tồn kho giữ nguyên.
9. Xem xác nhận đơn, chi tiết và tracking. Shipment mới ở PREPARING; timeline không tự giả lập giao hàng thành công.
10. Sản phẩm 24 hết hàng để demo unavailable; tìm `nonsensexyz` để demo empty state.

## Kiến trúc và dữ liệu

- `presentation/`: 5 controller bắt buộc; `web.py` là adapter FastAPI, schema và render HTML.
- `application/search/`: validate → normalize → retrieve qua ProductRepository → rank Top-K.
- `application/recommendation/`: content similarity, implicit peer interactions, hybrid ranking; cold-start dùng content.
- `application/commerce/`: giỏ hàng, checkout, payment simulation, order và shipment.
- `domain/`: các entity và enum của Chapter 4; không import HTTP/SQL/repository.
- `data/repository/`: ánh xạ bảng thành domain object.
- `data/infrastructure/`: ProductDatabase, OrderDatabase, VectorIndex, ImageStorage.
- `bootstrap.py`: composition root, inject dependency và bao toàn bộ use case trong SQLite transaction.
- `main.py`: application factory, static mounts, đăng ký routes.

Checkout dùng `BEGIN IMMEDIATE` để serialize thao tác tồn kho trong prototype SQLite; mọi ghi order/payment/shipment/cart/interaction cùng transaction. Nếu lỗi sau reserve, service release lượng đã reserve, transaction rollback toàn bộ khi exception thoát scope. Không có FK Cart–Order. Giá mua được lưu ở cột kỹ thuật `order_items.price_snapshot`, không thêm `unitPrice` vào domain.

Bảng: customers, categories, products, product_specifications, product_units, search_queries, text_queries, image_queries, voice_queries, search_results, interactions, carts, cart_items, orders, order_items, payments, shipments. `quantity_available` nằm trực tiếp trong `products`; `product_units` liên kết trực tiếp bằng `product_id`. Mọi truy vấn và kết quả tìm kiếm đều được lưu lịch sử.

Ứng dụng là demo cục bộ một khách hàng cố định (customerId=1), chưa có đăng nhập hoặc phân quyền nhiều người dùng. Không triển khai công khai với dữ liệu cá nhân thật. Các giá, mô tả và ảnh minh họa là dữ liệu mẫu tự tạo; không scrape website ngoài. Vector index nằm trong bộ nhớ; không cần API key hay model tải ngoài.

Xem `TRACEABILITY.md` để đối chiếu và chuẩn bị ảnh báo cáo. Kết quả chạy thực tế: `VERIFICATION.md` (52 kiểm thử đạt, 18 kiểm tra màn hình trên Chrome); ảnh minh chứng nằm trong `artifacts/`.

