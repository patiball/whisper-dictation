#!/usr/bin/env python3
"""
TDD Red Phase Runner
Runs all tests to demonstrate the Red phase - tests should FAIL initially.

This script executes the full TDD Red phase according to the test plan in testy.md.
"""

import sys
import subprocess
from pathlib import Path
import argparse

def run_command(cmd, description):
    """Run a command and capture output."""
    print(f"\n{'='*60}")
    print(f"🔴 RED PHASE: {description}")
    print(f"{'='*60}")
    print(f"Command: {' '.join(cmd)}")
    print("-" * 60)
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        print("STDOUT:")
        print(result.stdout)
        
        if result.stderr:
            print("\nSTDERR:")
            print(result.stderr)
        
        print(f"\nReturn code: {result.returncode}")
        
        return result.returncode == 0, result.stdout, result.stderr
        
    except subprocess.TimeoutExpired:
        print("❌ Command timed out (5 minutes)")
        return False, "", "Timeout"
    except Exception as e:
        print(f"❌ Command failed: {e}")
        return False, "", str(e)

def check_prerequisites():
    """Check if required dependencies are available."""
    print("🔍 Checking prerequisites...")
    
    # Check Python modules
    required_modules = [
        'pytest', 'pyaudio', 'librosa', 'numpy', 
        'whisper', 'psutil'
    ]
    
    missing = []
    for module in required_modules:
        try:
            __import__(module)
            print(f"✅ {module}")
        except ImportError:
            missing.append(module)
            print(f"❌ {module}")
    
    if missing:
        print(f"\n⚠️  Missing modules: {missing}")
        print("Install with: pip install " + " ".join(missing))
        return False
    
    # Check test audio files
    audio_dir = Path("tests/audio")
    audio_files = list(audio_dir.glob("test_*.wav")) if audio_dir.exists() else []
    
    print(f"\n📁 Test audio files: {len(audio_files)}")
    if len(audio_files) == 0:
        print("⚠️  No test audio files found. Run record_test_samples.py first.")
        return False
    
    for file in audio_files:
        print(f"   📄 {file.name}")
    
    return True

def run_red_phase_tests():
    """Run all TDD Red Phase tests."""
    
    print("\n" + "="*80)
    print("🔴 TDD RED PHASE - WHISPER DICTATION TESTS")
    print("="*80)
    print("Expected outcome: ALL TESTS SHOULD FAIL")
    print("This demonstrates the requirements before implementation.")
    print("="*80)
    
    if not check_prerequisites():
        print("\n❌ Prerequisites not met. Aborting Red phase.")
        return False
    
    test_suites = [
        {
            'name': 'Language Detection Tests',
            'file': 'tests/test_language_detection.py',
            'description': 'Testing language detection accuracy and text completeness'
        },
        {
            'name': 'Performance Tests', 
            'file': 'tests/test_performance.py',
            'description': 'Testing transcription speed and GPU acceleration'
        },
        {
            'name': 'Recording Quality Tests',
            'file': 'tests/test_recording_quality.py', 
            'description': 'Testing audio clipping and recording delays'
        }
    ]
    
    results = {}
    
    for suite in test_suites:
        print(f"\n\n{'#'*80}")
        print(f"📋 TEST SUITE: {suite['name']}")
        print(f"📝 {suite['description']}")
        print(f"📁 {suite['file']}")
        print('#'*80)
        
        cmd = [sys.executable, '-m', 'pytest', suite['file'], '-v', '--tb=short', '--no-header']
        
        success, stdout, stderr = run_command(cmd, f"Running {suite['name']}")
        
        results[suite['name']] = {
            'success': success,
            'stdout': stdout,
            'stderr': stderr
        }
        
        if success:
            print(f"⚠️  UNEXPECTED: {suite['name']} passed (should fail in Red phase)")
        else:
            print(f"✅ EXPECTED: {suite['name']} failed (Red phase working correctly)")
    
    # Summary
    print(f"\n\n{'='*80}")
    print("🔴 RED PHASE SUMMARY")
    print("="*80)
    
    total_suites = len(test_suites)
    failed_suites = sum(1 for r in results.values() if not r['success'])
    
    print(f"Total test suites: {total_suites}")
    print(f"Failed test suites: {failed_suites}")
    print(f"Passed test suites: {total_suites - failed_suites}")
    
    if failed_suites == total_suites:
        print("\n🎯 RED PHASE COMPLETE!")
        print("✅ All tests failed as expected")
        print("✅ Requirements are clearly defined")
        print("✅ Ready to proceed to GREEN PHASE (implementation)")
        
        print(f"\n📋 NEXT STEPS:")
        print("1. Analyze the test failures to understand requirements")
        print("2. Implement SpeechTranscriber class with required methods")
        print("3. Implement Recorder class with timestamp methods") 
        print("4. Fix language detection to support both English and Polish")
        print("5. Optimize performance to meet speed requirements")
        print("6. Fix audio clipping issues")
        print("7. Re-run tests to reach GREEN PHASE")
        
        return True
    else:
        print(f"\n⚠️  RED PHASE INCOMPLETE")
        print(f"Some tests passed unexpectedly. Review implementation.")
        
        for suite, result in results.items():
            status = "PASSED" if result['success'] else "FAILED"
            print(f"   {suite}: {status}")
        
        return False

def main():
    """Main function with command line interface."""
    parser = argparse.ArgumentParser(description="TDD Red Phase Test Runner")
    parser.add_argument('--audio-check', action='store_true', 
                       help='Only check for test audio files')
    parser.add_argument('--prerequisites', action='store_true',
                       help='Only check prerequisites')
    
    args = parser.parse_args()
    
    if args.prerequisites:
        success = check_prerequisites()
        sys.exit(0 if success else 1)
    
    if args.audio_check:
        audio_dir = Path("tests/audio")
        audio_files = list(audio_dir.glob("test_*.wav")) if audio_dir.exists() else []
        print(f"Test audio files found: {len(audio_files)}")
        
        if len(audio_files) == 0:
            print("❌ No test audio files. Run: python tests/record_test_samples.py")
            sys.exit(1)
        else:
            for file in audio_files:
                print(f"✅ {file.name}")
            sys.exit(0)
    
    success = run_red_phase_tests()
    
    if success:
        print("\n🎉 Red phase completed successfully!")
        print("Next: Implement fixes to reach Green phase")
    else:
        print("\n⚠️  Red phase had issues. Review output above.")
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
