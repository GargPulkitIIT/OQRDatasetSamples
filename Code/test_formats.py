#!/usr/bin/env python3
"""
Test script demonstrating multi-format image support for OQR encoder.
Tests encoding in various formats and verifies file creation.
"""

import os
import sys
from encoder import encode
from decoder import decode
from image_utils import list_supported_formats, get_image_extension

def test_single_format(name, qr_type, data1, data2, data3, format_type):
    """Test encoding in a single format."""
    print(f"\n📷 Testing {format_type.upper()} format...")
    try:
        if qr_type == "2":
            result = encode(name, "2", data3, data2, format=format_type)
        else:
            result = encode(name, "3", data3, data2, data1, format=format_type)
        
        if result and os.path.exists(result):
            size = os.path.getsize(result) / 1024  # Size in KB
            print(f"   SUCCESS: {result} ({size:.2f} KB)")
            return True
        else:
            print(f"    FAILED: File not created")
            return False
    except Exception as e:
        print(f"    ERROR: {e}")
        return False

def test_all_formats():
    """Test encoding in all supported formats."""
    print("=" * 60)
    print("OQR MULTI-FORMAT SUPPORT TEST")
    print("=" * 60)
    
 
    test_name_2 = "test_type2"
    test_name_3 = "test_type3"
    

    data2_val = "Hello"
    data3_val = "OQR"
    

    data1_val = "Type3"
    data2_val_3 = "Test"
    data3_val_3 = "Code"
    
    print("\n Supported Formats:")
    print("-" * 60)
    for fmt, desc in list_supported_formats().items():
        print(f"  • {fmt.upper():8} - {desc}")
    
    print("\n" + "=" * 60)
    print("TYPE 2 ENCODING TEST")
    print("=" * 60)
    print(f"Data: {data2_val}, {data3_val}")
    
    results_type2 = {}
    for fmt in sorted(list_supported_formats().keys()):
        results_type2[fmt] = test_single_format(
            test_name_2, "2", 
            None, data2_val, data3_val, 
            fmt
        )
    
    print("\n" + "=" * 60)
    print("TYPE 3 ENCODING TEST")
    print("=" * 60)
    print(f"Data: {data1_val}, {data2_val_3}, {data3_val_3}")
    
    results_type3 = {}
    for fmt in sorted(list_supported_formats().keys()):
        results_type3[fmt] = test_single_format(
            test_name_3, "3", 
            data1_val, data2_val_3, data3_val_3, 
            fmt
        )
    

    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    type2_pass = sum(1 for v in results_type2.values() if v)
    type2_total = len(results_type2)
    type3_pass = sum(1 for v in results_type3.values() if v)
    type3_total = len(results_type3)
    
    print(f"\nType 2 Results: {type2_pass}/{type2_total} formats passed")
    for fmt, passed in sorted(results_type2.items()):
        status = "" if passed else ""
        print(f"  {status} {fmt.upper()}")
    
    print(f"\nType 3 Results: {type3_pass}/{type3_total} formats passed")
    for fmt, passed in sorted(results_type3.items()):
        status = "" if passed else ""
        print(f"  {status} {fmt.upper()}")
    
    total_pass = type2_pass + type3_pass
    total_tests = type2_total + type3_total
    
    print(f"\n{'='*60}")
    print(f"OVERALL: {total_pass}/{total_tests} tests passed")
    print(f"{'='*60}\n")
    
    return total_pass == total_tests

def test_decoding():
    """Test decoding from different formats."""
    print("\n" + "=" * 60)
    print("DECODING TEST")
    print("=" * 60)
    
    test_name = "test_decode"
    data1 = "Value1"
    data2 = "Value2"
    data3 = "Value3"
    
    formats_to_test = ['png', 'jpg', 'webp']
    
    for fmt in formats_to_test:
        print(f"\n Encoding/Decoding with {fmt.upper()}...")
        
        output_path = encode(test_name, "3", data3, data2, data1, format=fmt)
        
        if output_path:
            try:
                v1, v2, v3 = decode(output_path)
                if v1 and v2 and v3:
                    print(f"   Decoded successfully:")
                    print(f"      V1: {v1}, V2: {v2}, V3: {v3}")
                else:
                    print(f"     Partial decode: V1={v1}, V2={v2}, V3={v3}")
            except Exception as e:
                print(f"    Decoding failed: {e}")
        else:
            print(f"   Encoding failed")

def test_format_validation():
    """Test format validation and fallback."""
    print("\n" + "=" * 60)
    print("FORMAT VALIDATION TEST")
    print("=" * 60)
    
    print("\n✓ Testing valid format (jpg)...")
    result = encode("test_valid", "2", "B", "A", format='jpg')
    print(f"  Result: {' Success' if result else ' Failed'}")
    
    print("\n✗ Testing invalid format (xyz) - should fallback to PNG...")
    result = encode("test_invalid", "2", "B", "A", format='xyz')
    if result and result.endswith('.png'):
        print(f"   Correctly fell back to PNG: {result}")
    else:
        print(f"   Unexpected result: {result}")

if __name__ == "__main__":
    try:
        success = test_all_formats()
        test_decoding()
        test_format_validation()
        
        if success:
            print("\n All format tests passed!")
            sys.exit(0)
        else:
            print("\n Some tests failed!")
            sys.exit(1)
    except Exception as e:
        print(f"\n Test execution failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
