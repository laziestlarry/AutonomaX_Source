# File: apps/api/config.py
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # API Settings
    API_HOST = os.getenv("API_HOST", "0.0.0.0")
    API_PORT = int(os.getenv("API_PORT", "8080"))
    
    # Database
    DATABASE_URL = os.getenv("DATABASE_URL")
    
    # External Services
    SHOPIFY_TOKEN = os.getenv("SHOPIFY_ADMIN_TOKEN")
    SHOPIFY_DOMAIN = os.getenv("SHOPIFY_SHOP_DOMAIN")
    
    # AI Providers
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    
config = Config()