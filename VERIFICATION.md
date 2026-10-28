# Kết quả kiểm chứng

Đã kiểm tra trong môi trường Windows, Python 3.14.2, Chrome headless và Node.js 24.13.0.

## Backend và kiến trúc

Lệnh thực tế trong môi trường có nhiều pytest plugin cài sẵn:

```powershell
$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD = '1'
python -m pytest -q --tb=short -p no:cacheprovider
```

Kết quả: **52 passed in 12.17s**.

- Text, voice transcript và image search; ranking deterministic, budget/brand/availability filters.
- Upload sai định dạng, giả MIME, file hỏng, quá 5 MB và path traversal bị từ chối.
- Add/update/remove cart, Decimal total, quantity validation, product stock reserve/release.
- COD, simulated card, simulated e-wallet; payment failure và lỗi ghi shipment rollback toàn bộ.
- Hai checkout đồng thời chỉ một giao dịch thành công khi tồn kho không đủ cho cả hai.
- Giá đơn hàng giữ nguyên khi giá catalog thay đổi.
- Persistence specifications, tồn kho và serial number.
- Recommendation loại sản phẩm hiện tại/hết hàng, có cold-start và collaborative signal.
- HTTP routes chính, order success/detail/tracking, static assets và HTML escaping.
- AST audit kiểm tra đủ lớp bắt buộc và không có dependency bị cấm.
- Python compileall và Node syntax check đã chạy thành công.

## Trình duyệt thực

Chạy `node tests/browser_smoke.mjs` với Python có đủ dependency. Script đã khởi động Uvicorn, chạy Chrome và dừng các tiến trình do nó tạo.

Kết quả: **18 kiểm tra màn hình**, **0 JavaScript exceptions**, **0 ảnh lỗi**, **0 trang tràn ngang** ở viewport 1440, 768 và 390 pixel.

Các tương tác đã chạy bằng JavaScript của giao diện: thêm giỏ, thay số lượng, đặt đơn, mở voice dialog và gửi transcript fallback. Browser test dùng dữ liệu tạm riêng.

Ảnh đã mở kiểm tra trực quan: `artifacts/home-desktop.png`, `artifacts/home-390.png`.

Các ảnh khác: cart-desktop, checkout-desktop, order-success-desktop, search-390, tracking-390. Kết quả chi tiết lưu tại `artifacts/browser-report.json`.

Sau kiểm tra trình duyệt, thay đổi cuối chỉ bổ sung type hints, xử lý lỗi HTTP, ánh xạ persistence và kiểm thử; toàn bộ 52 kiểm thử backend đã chạy lại. Giao diện CSS/HTML/JS không thay đổi sau lần kiểm tra browser thành công.

## Giới hạn đã biết

- Microphone thực chưa kiểm tra với thiết bị âm thanh; transcript fallback đã kiểm tra trên browser.
- Image matching là color/texture, không phải nhận dạng đối tượng AI.
- Ảnh là minh họa; dữ liệu, thanh toán, khách hàng và shipment là demo.
- Không tự động chuyển shipment sang Delivered; không có giao dịch thanh toán thật.
- Server kiểm chứng đã dừng; dùng lệnh trong README để mở ứng dụng demo.
