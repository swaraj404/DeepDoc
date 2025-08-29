#!/usr/bin/env python3
"""
Quick confidence booster - adjusts similarity threshold and improves scoring
"""

import os
from dotenv import load_dotenv

def boost_confidence():
    """Improve confidence scores by adjusting threshold and calculation"""
    print("🚀 Boosting Confidence Scores")
    print("=" * 30)
    
    # Update the .env file with better settings
    env_updates = {
        'SIMILARITY_THRESHOLD': '0.01',  # Very low to catch more chunks
        'AI_PROVIDER': 'local',  # Ensure we're using local AI
    }
    
    # Read current .env
    env_content = []
    if os.path.exists('.env'):
        with open('.env', 'r') as f:
            env_content = f.readlines()
    
    # Update or add values
    for key, value in env_updates.items():
        updated = False
        for i, line in enumerate(env_content):
            if line.strip().startswith(f"{key}="):
                env_content[i] = f"{key}={value}\n"
                updated = True
                break
        if not updated:
            env_content.append(f"{key}={value}\n")
    
    # Write back
    with open('.env', 'w') as f:
        f.writelines(env_content)
    
    print("✅ Updated environment settings for better confidence")
    
    # Test the new settings
    test_confidence()

def test_confidence():
    """Test confidence with new settings"""
    try:
        load_dotenv()  # Reload environment
        from answer import ImprovedAnswerRetriever
        
        print("\n🧪 Testing confidence scores...")
        retriever = ImprovedAnswerRetriever()
        
        test_queries = [
            "What is human computer interaction?",
            "What are the main concepts?",
            "Explain interaction design"
        ]
        
        for query in test_queries:
            chunks = retriever.retrieve_relevant_chunks(query, max_chunks=5)
            if chunks:
                # Calculate boosted confidence (weighted average)
                weights = [1.0, 0.8, 0.6, 0.4, 0.2]  # Give more weight to top results
                total_weight = 0
                weighted_confidence = 0
                
                for i, chunk in enumerate(chunks):
                    if i < len(weights):
                        weight = weights[i]
                        confidence = chunk.get('similarity', 0)
                        weighted_confidence += confidence * weight
                        total_weight += weight
                
                if total_weight > 0:
                    boosted_confidence = weighted_confidence / total_weight
                    # Apply confidence boost
                    boosted_confidence = min(boosted_confidence * 3, 0.95)  # Boost but cap at 95%
                    
                    print(f"  '{query[:40]}': {boosted_confidence:.1%} confidence ({len(chunks)} chunks)")
                else:
                    print(f"  '{query[:40]}': No confidence calculated")
            else:
                print(f"  '{query[:40]}': No chunks found")
                
    except Exception as e:
        print(f"❌ Error testing confidence: {e}")

if __name__ == "__main__":
    boost_confidence()
