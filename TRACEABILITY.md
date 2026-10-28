# Chapter 4.5 — Traceability

| Nội dung Chapter 4 | Mã triển khai | Minh chứng demo |
|---|---|---|
| Presentation controllers | presentation/*_controller.py | GET /search, /cart, /orders/{id} |
| Search orchestration | application/search/search_service.py | Text, voice và image cùng pipeline |
| Query inheritance | domain/search/*_query.py | TextQuery, VoiceQuery, ImageQuery kế thừa SearchQuery |
| Local retrieval | application/search/retrieval_service.py | Truy cập ProductRepository; không gọi infrastructure |
| Ranking | application/search/ranking_service.py | Rank, relevanceScore, product; bộ lọc backend |
| Recommendation | application/recommendation/recommendation_service.py | Home, product detail, cart |
| Domain behavior | domain/cart/cart.py; domain/product/product.py | Quantity, total, reserve/release |
| Checkout orchestration | application/commerce/checkout_service.py | Success và simulated failure |
| Persistence isolation | data/repository/*_repository.py | Repository trả domain object |
| Physical database | data/infrastructure/product_database.py; order_database.py | runtime/electronics.db |
| Shipment | domain/order/shipment.py; application/commerce/order_service.py | /orders/{id}/tracking |
| Architecture audit | tests/test_architecture.py | AST forbidden-import check, required classes |
| Runtime/UI verification | tests/test_web.py; tests/browser_smoke.mjs | HTTP flow, desktop/mobile, browser JS |

## Các lớp bắt buộc

- Presentation: SearchController, RecommendationController, CartController, CheckoutController, OrderController.
- Search: SearchService, QueryProcessor, SpeechToTextService, TextEmbeddingService, ImageEmbeddingService, RetrievalService, RankingService.
- Recommendation: RecommendationService, ContentBasedRecommender, CollaborativeRecommender, HybridRankingService.
- Commerce: CartService, CheckoutService, OrderService.
- Domain: Customer; SearchQuery, TextQuery, ImageQuery, VoiceQuery, SearchResult; Product, ProductSpecification, Category, ProductUnit; Interaction; Cart, CartItem; Order, OrderItem, Payment, Shipment.
- Repository: ProductRepository, SearchRepository, InteractionRepository, CartRepository, OrderRepository, PaymentRepository, ShipmentRepository.
- Infrastructure: ProductDatabase, OrderDatabase, VectorIndex, ImageStorage.

Request schema QuantityInput, Bootstrap và adapter web không phải domain entity mới.

## Gợi ý chụp báo cáo

1. Source tree trong IDE.
2. SearchController.search và SearchService.search.
3. Cart.addItem/calculateTotal và Product.reserve/release.
4. ProductRepository.findById và schema SQLite.
5. Trang chủ desktop và mobile.
6. Text search, voice transcript, image preview/results.
7. Product detail với specifications/recommendations.
8. Giỏ hàng và checkout.
9. Order confirmation, detail và shipment tracking.
10. Kết quả pytest và browser-report.json.

## Giới hạn prototype được công khai

- Ảnh sản phẩm là minh họa lập trình; image matching dựa trên màu/texture.
- Nhận dạng giọng nói phụ thuộc browser; transcript mô phỏng là fallback offline.
- Payment, delivery và customer đều là demo; không tích hợp gateway hoặc vận chuyển thật.
- Search results không lưu lâu dài; danh sách bảng search trong đặc tả là gợi ý.
- ShipmentRepository.save và PaymentRepository.save nhận thêm orderId để lưu FK của relationship; domain không chứa cột persistence phụ.
- Các ID customerId ở Cart/Order thể hiện relationship Customer của UML, không tạo domain entity mới.

