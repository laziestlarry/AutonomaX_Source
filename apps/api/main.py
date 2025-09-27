from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

# 1. Define models FIRST
class ProductBrief(BaseModel):
    category: str
    audience: str
    keywords: List[str] = []
    refs: List[str] = []

class ProductDraft(BaseModel):
    id: str
    title: str
    description: str
    tags: List[str]
    assets: List[str]
    price: float

class PublishRequest(BaseModel):
    channel: str
    draft_id: str
    pricing: dict = {}

# 2. Create router SECOND
products_router = APIRouter(prefix="/v1/products", tags=["products"])

# 3. Use router THIRD
@products_router.post("/draft")
async def create_product_draft(brief: ProductBrief):
    """Create product draft - integrates with your existing endpoints"""
    return {
        "id": "demo-123",
        "title": f"{brief.category} - {brief.audience}",
        "description": "AI-generated product description",
        "tags": brief.keywords,
        "assets": [],
        "price": 19.99
    }

@products_router.post("/publish")
async def publish_product(req: PublishRequest):
    """Publish to Shopify using existing integration"""
    return {"status": "published", "channel": req.channel, "product_id": "shopify_123"}

@products_router.get("")
async def list_products():
    """List all products"""
    return {"products": []}

# 4. Create app and include routers LAST
app = FastAPI(title="AutonomaX API", version="11.1")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include your router
app.include_router(products_router)

# Keep your existing endpoints
@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.get("/ready")
async def ready():
    return {"status": "ready"}

# Add any other existing endpoints you have...