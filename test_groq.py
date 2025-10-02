#!/usr/bin/env python3
"""Test Groq API directly"""

from openai import OpenAI
import os

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

def test_groq_api():
    """Test Groq API directly"""
    
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        print("❌ No GROQ_API_KEY found")
        return False
    
    print(f"🔑 Using API key: {api_key[:10]}...")
    
    try:
        client = OpenAI(
            api_key=api_key,
            base_url="https://api.groq.com/openai/v1"
        )
        
        print("🔄 Testing Groq API connection...")
        
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {
                    "role": "system",
                    "content": "You are an accessibility expert."
                },
                {
                    "role": "user",
                    "content": "Generate a brief remediation suggestion for a missing alt text issue."
                }
            ],
            max_tokens=100,
            temperature=0.3
        )
        
        suggestion = response.choices[0].message.content.strip()
        print("✅ Groq API working!")
        print(f"   Response: {suggestion}")
        return True
        
    except Exception as e:
        print(f"❌ Groq API error: {str(e)}")
        return False

if __name__ == "__main__":
    print("🧪 Groq API Test")
    print("=" * 20)
    test_groq_api()
