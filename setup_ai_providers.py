#!/usr/bin/env python3
"""
AI Provider Setup Guide for DeepDoc
This script helps you set up alternative AI providers
"""

import os
from dotenv import load_dotenv

load_dotenv()

def print_setup_guide():
    """Print setup instructions for all AI providers"""
    print("\n🤖 AI Provider Setup Guide for DeepDoc")
    print("=" * 60)
    
    print("\n1. 🥇 OpenAI GPT (RECOMMENDED)")
    print("   ✅ Most reliable and fast")
    print("   💰 Free tier: $5 credit for new users")
    print("   🔗 Get API key: https://platform.openai.com/api-keys")
    print("   📝 Steps:")
    print("      1. Create account at https://platform.openai.com/")
    print("      2. Go to API Keys section")
    print("      3. Create new API key")
    print("      4. Add to .env: OPENAI_API_KEY=your_key_here")
    print("      5. Set AI_PROVIDER=openai in .env")
    
    print("\n2. 🥈 Anthropic Claude")
    print("   ✅ High quality responses")
    print("   💰 Free tier: $5 credit for new users")
    print("   🔗 Get API key: https://console.anthropic.com/")
    print("   📝 Steps:")
    print("      1. Create account at https://console.anthropic.com/")
    print("      2. Get API key from dashboard")
    print("      3. Add to .env: ANTHROPIC_API_KEY=your_key_here")
    print("      4. Set AI_PROVIDER=anthropic in .env")
    
    print("\n3. 🥉 Google Gemini (Currently Limited)")
    print("   ⚠️  Currently has quota issues")
    print("   🔗 Get API key: https://makersuite.google.com/app/apikey")
    print("   📝 Steps:")
    print("      1. Go to Google AI Studio")
    print("      2. Create new project")
    print("      3. Generate API key")
    print("      4. Set AI_PROVIDER=google in .env")
    
    print("\n4. 🏠 Local Models (No API Key Required)")
    print("   ✅ Completely free")
    print("   ⚠️  Requires good hardware (4GB+ RAM)")
    print("   📝 Steps:")
    print("      1. Set AI_PROVIDER=local in .env")
    print("      2. First run will download the model")
    print("      3. Enable GPU with USE_GPU=true if available")

def test_provider(provider_name):
    """Test if a provider is working"""
    try:
        from answer import ImprovedAnswerRetriever
        
        # Temporarily set the provider
        os.environ['AI_PROVIDER'] = provider_name
        
        print(f"\n🧪 Testing {provider_name} provider...")
        retriever = ImprovedAnswerRetriever()
        
        # Test with a simple prompt
        test_response = retriever.call_ai_with_retry("Hello, can you respond with 'AI working correctly'?")
        
        if test_response:
            print(f"✅ {provider_name} is working!")
            print(f"📝 Response: {test_response[:100]}...")
            return True
        else:
            print(f"❌ {provider_name} failed to respond")
            return False
            
    except Exception as e:
        print(f"❌ {provider_name} failed: {e}")
        return False

def check_current_setup():
    """Check what providers are currently available"""
    print("\n🔍 Checking Current Setup")
    print("-" * 30)
    
    # Check environment variables
    openai_key = os.getenv('OPENAI_API_KEY')
    google_key = os.getenv('GOOGLE_API_KEY')
    anthropic_key = os.getenv('ANTHROPIC_API_KEY')
    current_provider = os.getenv('AI_PROVIDER', 'openai')
    
    print(f"Current provider: {current_provider}")
    print(f"OpenAI key: {'✅ Set' if openai_key and openai_key != 'your_openai_api_key_here' else '❌ Not set'}")
    print(f"Google key: {'✅ Set' if google_key else '❌ Not set'}")
    print(f"Anthropic key: {'✅ Set' if anthropic_key else '❌ Not set'}")
    
    # Check packages
    try:
        import openai
        print("OpenAI package: ✅ Installed")
    except ImportError:
        print("OpenAI package: ❌ Not installed")
    
    try:
        import anthropic
        print("Anthropic package: ✅ Installed")
    except ImportError:
        print("Anthropic package: ❌ Not installed")
    
    try:
        import transformers
        print("Transformers package: ✅ Installed")
    except ImportError:
        print("Transformers package: ❌ Not installed")

def interactive_setup():
    """Interactive setup for AI providers"""
    print("\n🛠️  Interactive Setup")
    print("-" * 20)
    
    print("\nWhich AI provider would you like to use?")
    print("1. OpenAI GPT (Recommended)")
    print("2. Anthropic Claude")
    print("3. Google Gemini")
    print("4. Local Model (Free)")
    
    choice = input("\nEnter your choice (1-4): ").strip()
    
    if choice == "1":
        api_key = input("Enter your OpenAI API key: ").strip()
        if api_key:
            update_env_file("OPENAI_API_KEY", api_key)
            update_env_file("AI_PROVIDER", "openai")
            print("✅ OpenAI configured!")
    
    elif choice == "2":
        api_key = input("Enter your Anthropic API key: ").strip()
        if api_key:
            update_env_file("ANTHROPIC_API_KEY", api_key)
            update_env_file("AI_PROVIDER", "anthropic")
            print("✅ Anthropic configured!")
    
    elif choice == "3":
        api_key = input("Enter your Google API key: ").strip()
        if api_key:
            update_env_file("GOOGLE_API_KEY", api_key)
            update_env_file("AI_PROVIDER", "google")
            print("✅ Google configured!")
    
    elif choice == "4":
        update_env_file("AI_PROVIDER", "local")
        print("✅ Local model configured!")
    
    else:
        print("❌ Invalid choice")

def update_env_file(key, value):
    """Update .env file with new value"""
    env_path = ".env"
    
    # Read current content
    lines = []
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            lines = f.readlines()
    
    # Update or add the key
    key_found = False
    for i, line in enumerate(lines):
        if line.strip().startswith(f"{key}="):
            lines[i] = f"{key}={value}\n"
            key_found = True
            break
    
    if not key_found:
        lines.append(f"{key}={value}\n")
    
    # Write back
    with open(env_path, 'w') as f:
        f.writelines(lines)

def main():
    """Main function"""
    print_setup_guide()
    check_current_setup()
    
    print("\n" + "=" * 60)
    print("Choose an option:")
    print("1. Interactive setup")
    print("2. Test current provider")
    print("3. Exit")
    
    choice = input("\nEnter your choice (1-3): ").strip()
    
    if choice == "1":
        interactive_setup()
    elif choice == "2":
        current_provider = os.getenv('AI_PROVIDER', 'openai')
        test_provider(current_provider)
    elif choice == "3":
        print("👋 Goodbye!")
    else:
        print("❌ Invalid choice")

if __name__ == "__main__":
    main()
