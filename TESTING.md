# Hướng dẫn kiểm thử ABC Electronics

## 1. Cài đặt và chạy ứng dụng

```powershell
cd D:\HTTT_TieuLuan\abc-electronics
python -m pip install -r requirements.txt
python -m uvicorn main:app --host 127.0.0.1 --port 8000
```

Mở `http://127.0.0.1:8000`.

## 2. Cấu hình AI

File `.env` không được đưa lên Git. Có thể tạo từ `.env.example`:

```text
OPENAI_API_KEY=your-key
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
OPENAI_FILTER_MODEL=gpt-4o-mini
OPENAI_RERANK_MODEL=gpt-4o-mini
AI_IMAGE_MODE=siglip
LOCAL_IMAGE_MODEL=Marqo/marqo-fashionSigLIP
AI_DETECT_MODE=owlvit
LOCAL_DETECTOR_MODEL=google/owlvit-base-patch32
OPENAI_TRANSCRIPTION_MODEL=gpt-transcribe
```

- Text/voice/image+text search dùng regex + OpenAI structured output để extract filter giá/brand/danh mục/màu/còn hàng, sau đó dùng `text-embedding-3-small` lấy ứng viên cosine `> 0,2`, rồi `gpt-4o-mini` rerank tối đa 20 sản phẩm; điểm dưới 50/100 bị loại. Truy vấn chỉ có filter bỏ qua bước cosine nhưng vẫn rerank. Filter extraction, embedding và reranking cần API key/kết nối mạng; lỗi API được báo rõ. Image-only vẫn dùng SigLIP/local visual search và không gọi filter extractor khi không có text.
- `AI_IMAGE_MODE=siglip`: chỉ dùng model `Marqo/marqo-fashionSigLIP` khi model đã có trong Hugging Face cache.
- `AI_IMAGE_MODE=basic`: dùng histogram màu và texture, không cần model.
- Ứng dụng không tự tải model ảnh. Nếu cache SigLIP không tồn tại hoặc không load được, hệ thống tự dùng `basic`.
- `AI_DETECT_MODE=owlvit`: dùng OWL-ViT đã có trong cache để tìm vật thể điện tử trong ảnh; nếu không có model, ảnh toàn phần vẫn tìm được. `AI_DETECT_MODE=off` tắt bước detect.
- Voice: ghi âm/tải WebM, WAV, MP3, MP4 hoặc M4A, server dùng `gpt-transcribe` khi có API key. Có thể nhập transcript thủ công nếu microphone hoặc API không dùng được.

## 3. Kiểm thử thủ công

1. Text search: nhập `gaming laptop`; kết quả đầu tiên phải là `ASUS ROG Strix G16`.
2. Budget search: nhập `phone under 20 million`; kết quả phải có giá không quá 20 triệu đồng.
   Có thể nhập `chuột` hoặc `chuột không dây` để tìm Logitech MX Master 3S; `điện thoại` trả về nhóm Smartphones.
3. Image search: tải `static/images/products/product-4.png`; kết quả đầu tiên phải là `Samsung Galaxy S24`.
4. Voice search: chọn Voice, đọc hoặc nhập `wireless noise cancelling headphones`; kết quả đầu tiên phải là `Sony WH-1000XM5`.
5. Image + text: tải `static/images/products/product-4.png`, nhập `Samsung phone`, bấm Find similar products; trang kết quả hiển thị `Image + text search`.
6. Object detection: tải ảnh, chờ khung phát hiện tự xuất hiện, chọn khung Smartphone rồi tìm; ảnh được crop theo vùng đã chọn. Không chọn khung hoặc bấm lại khung đang chọn thì tìm bằng toàn ảnh. Nếu model chưa có trong cache, giao diện báo rõ và vẫn tìm bằng toàn ảnh.
7. Recommendation: mở chi tiết một sản phẩm; khu vực gợi ý phải hiển thị tối đa bốn sản phẩm còn hàng và không lặp sản phẩm đang xem.
8. Cart: thêm sản phẩm, cập nhật số lượng và xóa sản phẩm.
9. Checkout: đặt hàng COD; kiểm tra order, payment, shipment và số lượng sản phẩm giảm.
10. Rollback: chọn card/e-wallet và bật simulated failure; giỏ hàng và số lượng sản phẩm phải giữ nguyên.
11. Tracking: mở đơn hàng vừa tạo; shipment phải có mã `ABC-...` và trạng thái `PREPARING`.

## 4. Chạy test tự động

```powershell
$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD='1'
python -m pytest -q --tb=short -p no:cacheprovider
```

Test tự động giả lập kết quả text embedding và dùng image embedding local để không gửi dữ liệu sản phẩm lên API hay phát sinh chi phí.

Kiểm tra trình duyệt thật:

```powershell
$env:ABC_PYTHON=(Get-Command python).Source
node tests/browser_smoke.mjs
```

## 5. Kiểm tra SQLite

Database thật nằm tại `runtime/electronics.db`. Sau khi thao tác trên giao diện, refresh DBeaver và kiểm tra:

- `search_queries`, `text_queries`, `image_queries`, `voice_queries`, `search_results`;
- `interactions`, `carts`, `cart_items`;
- `orders`, `order_items`, `payments`, `shipments`;
- `products.quantity_available`.
