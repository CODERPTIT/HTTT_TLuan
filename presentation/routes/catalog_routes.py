import json
from decimal import Decimal
from urllib.parse import urlencode

from fastapi import File, Query, Request, UploadFile, Form
from fastapi.responses import RedirectResponse
from starlette.concurrency import run_in_threadpool

from domain.search.image_query import ImageQuery
from domain.search.search_result import SearchResult
from domain.search.voice_query import VoiceQuery


def register_catalog_routes(app, web):
    @app.get("/")
    def home(request: Request):
        with web.scope(request) as services:
            identity = web.optionalCustomerId(request, services)
            products = services.search.catalog()
            category_products = []
            seen_categories = set()
            for product in products:
                category = product.category.categoryName
                if category not in seen_categories:
                    category_products.append(product)
                    seen_categories.add(category)
            recently_viewed = []
            viewed_ids = set()
            if identity is not None:
                for interaction in reversed(services.recommendation.service.getInteractionHistory(identity)):
                    product = interaction.product
                    if interaction.interactionType == "VIEW" and product.productId not in viewed_ids:
                        recently_viewed.append(product)
                        viewed_ids.add(product.productId)
            return web.render(request, "home.html", products=products[:10], deals=products[10:15],
                categories=sorted({product.category.categoryName for product in products}),
                category_products=category_products, recently_viewed=recently_viewed[:5],
                recommendations=services.recommendation.getRecommendations(identity or 0, 1))

    @app.get("/search")
    def search(request: Request, q: str = "", category: str = "", brand: str = "", color: str = "",
               minimum: Decimal = Query(0, ge=0), maximum: Decimal | None = Query(None, ge=0),
               available: bool = False, sort: str = "relevance", image: str = "", transcript: str = ""):
        with web.scope(request) as services:
            web.optionalCustomerId(request, services)
            if image:
                results = services.search.search(ImageQuery(imageReference=image, queryText=q))
                modality, summary = ("Image + text", q) if q else ("Image", "Visual matches")
                backend = services.search.service.ranking.image.backend
                ranking_label = ("visual similarity and OpenAI reranking" if q else
                                 "SigLIP visual search" if backend == "siglip" else "local visual fallback")
            elif transcript:
                results = services.search.search(VoiceQuery(transcribedText=transcript))
                modality, summary = "Voice", transcript
                ranking_label = "OpenAI embeddings and reranking"
            elif q.strip().lower() in {"", "electronics"}:
                results = [SearchResult(index, Decimal(0), product)
                           for index, product in enumerate(services.search.catalog(), 1)]
                modality, summary, ranking_label = "Browse", "All electronics", "catalog order"
            else:
                results = services.search.text(q)
                modality, summary, ranking_label = "Text", q, "OpenAI embeddings and reranking"
            catalog = services.search.catalog()
            results = services.search.filterResults(results, category, brand, minimum, maximum, available, sort, color)
            colors = sorted({spec.specValue for product in catalog for spec in product.specifications
                             if spec.specName == "Color"})
            return web.render(request, "search_results.html", results=results, modality=modality, summary=summary,
                ranking_label=ranking_label, q=q, image=image, transcript=transcript, category=category, brand=brand,
                color=color, minimum=minimum, maximum=maximum, available=available, sort=sort,
                categories=sorted({product.category.categoryName for product in catalog}),
                brands=sorted({product.brand for product in catalog}), colors=colors)

    @app.post("/search/detect")
    async def detect_objects(request: Request, image: UploadFile = File(...)):
        if image.content_type not in {"image/jpeg", "image/png", "image/webp"}:
            raise ValueError("Upload a JPG, PNG or WebP image")
        content = await image.read(5 * 1024 * 1024 + 1)
        with web.scope(request) as services:
            objects = await run_in_threadpool(services.object_detector.detect, content)
            return {"available": services.object_detector.available, "objects": objects}

    @app.post("/search/image")
    async def image_search(request: Request, image: UploadFile = File(...), q: str = Form(""),
                           crop_box: str = Form("")):
        content = await image.read(5 * 1024 * 1024 + 1)
        if len(q) > 500:
            raise ValueError("Enter a search query of up to 500 characters")
        try:
            box = json.loads(crop_box) if crop_box else None
        except json.JSONDecodeError as error:
            raise ValueError("Invalid crop area") from error
        with web.scope(request) as services:
            reference = services.search.uploadImage(content, image.filename or "", image.content_type or "", box)
        return RedirectResponse("/search?" + urlencode({"image": reference, "q": q}), status_code=303)

    @app.post("/search/voice")
    def voice_search(request: Request, transcript: str = Form(...)):
        if not transcript.strip() or len(transcript) > 500:
            raise ValueError("Enter a search query of up to 500 characters")
        return RedirectResponse("/search?" + urlencode({"transcript": transcript}), status_code=303)

    @app.post("/search/transcribe")
    async def transcribe_audio(request: Request, audio: UploadFile = File(...)):
        content = await audio.read(10 * 1024 * 1024 + 1)
        with web.scope(request) as services:
            transcript = await run_in_threadpool(services.speech.transcribeAudio,
                                                 content, audio.filename or "", audio.content_type or "")
        return {"transcript": transcript}

    @app.get("/products/{productId}")
    def product_detail(request: Request, productId: int):
        if productId <= 0:
            raise ValueError("Invalid product ID")
        with web.scope(request) as services:
            identity = web.optionalCustomerId(request, services)
            product = services.search.product(productId, identity)
            return web.render(request, "product_detail.html", product=product,
                recommendations=services.recommendation.getRecommendations(identity or 0, productId))

    @app.get("/api/recommendations")
    def recommendations(request: Request, productId: int = Query(1, gt=0)):
        with web.scope(request) as services:
            identity = web.optionalCustomerId(request, services)
            return services.recommendation.getRecommendations(identity or 0, productId)
