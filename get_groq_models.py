#!/usr/bin/env python3
"""Script to get available Groq models"""

import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_groq_models():
    """Get available models from Groq API"""
    
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        print("❌ No GROQ_API_KEY found")
        return False
    
    print(f"🔑 Using API key: {api_key[:10]}...")
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    try:
        print("🔄 Fetching available models from Groq...")
        
        response = requests.get(
            "https://api.groq.com/openai/v1/models",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            models_data = response.json()
            models = models_data.get("data", [])
            
            print(f"✅ Found {len(models)} available models:")
            print("=" * 50)
            
            for model in models:
                model_id = model.get("id", "Unknown")
                owner = model.get("owned_by", "Unknown")
                created = model.get("created", "Unknown")
                
                print(f"📋 Model: {model_id}")
                print(f"   Owner: {owner}")
                print(f"   Created: {created}")
                print()
            
            # List just the model IDs for easy reference
            print("🎯 Model IDs for easy copy-paste:")
            print("-" * 30)
            for model in models:
                print(f"'{model.get('id')}'")
            
            return True
            
        else:
            print(f"❌ Failed to fetch models: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error fetching models: {str(e)}")
        return False

if __name__ == "__main__":
    print("🧪 Groq Models Fetcher")
    print("=" * 25)
    get_groq_models()
