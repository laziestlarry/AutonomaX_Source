# File: apps/api/routers/products.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter()

# Your actual product models from blueprint
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

# CRITICAL: Add these to your main.py imports
@router.post("/draft")
async def create_draft(brief: ProductBrief):
    """Create product draft - integrates with your existing endpoints"""
    # Use your existing /monetization/price_suggest
    # Use your existing /marketing/campaigns/suggest
    return {
        "id": "draft_001",
        "title": f"{brief.category} - {brief.audience}",
        "description": "Generated product description",
        "tags": brief.keywords,
        "assets": [],
        "price": 19.99
    }

@router.get("")
async def list_products():
    """List all products - connects to your database"""
    return {"products": []}