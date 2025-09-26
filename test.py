#!/usr/bin/env python3
"""
Test script for the FACEIT Name Checker
"""

from check import FaceitNameChecker

def test_random_word_api():
    """Test the Random Word API integration"""
    print("Testing Random Word API integration...")
    checker = FaceitNameChecker()
    
    # Test fetching 3-letter words
    print("\n1. Testing 3-letter word fetch:")
    words_3 = checker.fetch_random_words(3, 10)
    print(f"Sample 3-letter words: {words_3[:5]}")
    
    # Test fetching 4-letter words
    print("\n2. Testing 4-letter word fetch:")
    words_4 = checker.fetch_random_words(4, 10)
    print(f"Sample 4-letter words: {words_4[:5]}")
    
    return words_3 + words_4

def test_faceit_api():
    """Test the FACEIT API with known names"""
    print("\n3. Testing FACEIT API with sample names:")
    print("   Note: This test creates temporary persistence files")
    
    # For testing, use a temporary checker without real cookies
    checker = FaceitNameChecker()
    
    # Test with some names that are likely available/unavailable
    test_names = ["smirk", "test", "xyz", "qwe", "abc"]
    
    for name in test_names:
        result = checker.check_name_availability(name)
        status = "✓ AVAILABLE" if result['available'] else "✗ TAKEN"
        idle_text = " (idle user)" if result['belongs_to_idle_user'] else ""
        print(f"  {name}: {status}{idle_text}")
    
    # Clean up test files
    import os
    try:
        if os.path.exists("checked_names.txt"):
            os.remove("checked_names.txt")
        if os.path.exists("available_names.txt"):
            os.remove("available_names.txt")
        print("   ✓ Cleaned up test files")
    except:
        pass

def main():
    print("FACEIT Name Checker - Test Suite")
    print("=" * 40)
    
    # Test 1: Random Word API
    sample_words = test_random_word_api()
    
    # Test 2: FACEIT API
    test_faceit_api()
    
    # Test 3: Check a few random words from the API
    if sample_words:
        print(f"\n4. Testing FACEIT availability for {len(sample_words[:5])} random words:")
        checker = FaceitNameChecker()
        
        for word in sample_words[:5]:
            result = checker.check_name_availability(word)
            status = "✓ AVAILABLE" if result['available'] else "✗ TAKEN"
            idle_text = " (idle user)" if result['belongs_to_idle_user'] else ""
            print(f"  {word}: {status}{idle_text}")
    
    print("\nTest completed! If you see words above, the integration is working.")
    print("Run 'python check.py' to start the full name checker.")

if __name__ == "__main__":
    main()
