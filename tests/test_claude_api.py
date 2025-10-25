"""
Test Claude API Connection
"""
import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()


def test_claude_api():
    """Basic Claude API test"""
    print("=" * 70)
    print("🔧 UAE Legal Agent - Claude API Test")
    print("=" * 70)
    
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("❌ ERROR: ANTHROPIC_API_KEY not found!")
        return
    
    print(f"✅ API Key loaded: {api_key[:20]}...")
    print("\n📤 Sending test request...")
    
    try:
        client = Anthropic(api_key=api_key)
        
        message = client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=1024,
            messages=[
                {
                    "role": "user",
                    "content": "Ahoj! Toto je test spojenia z ICC Komárno Legal Agent. Môžeš odpovedať po slovensky?"
                }
            ]
        )
        
        response_text = message.content[0].text
        
        print("\n" + "=" * 70)
        print("📥 Response from Claude:")
        print("=" * 70)
        print(response_text)
        print("=" * 70)
        
        print(f"\n📊 Token Usage:")
        print(f"   Input:  {message.usage.input_tokens:,}")
        print(f"   Output: {message.usage.output_tokens:,}")
        print(f"   Total:  {message.usage.input_tokens + message.usage.output_tokens:,}")
        
        input_cost = (message.usage.input_tokens / 1_000_000) * 3
        output_cost = (message.usage.output_tokens / 1_000_000) * 15
        total_cost = input_cost + output_cost
        
        print(f"\n💰 Cost: ${total_cost:.6f}")
        print(f"💳 Free Credit Remaining: ~${5.00 - total_cost:.4f}")
        
        print("\n✅ TEST SUCCESSFUL! Claude API is working.")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")


if __name__ == "__main__":
    test_claude_api()
