#!/usr/bin/env python3
"""
Test script to verify Ollama and configured model setup
Tests connection, model availability, and scoring functionality
"""

import sys
import time
import requests
import json
import os
from pathlib import Path

# Color codes for output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}\n")

def print_success(text):
    print(f"{Colors.GREEN}✓{Colors.END} {text}")

def print_error(text):
    print(f"{Colors.RED}✗{Colors.END} {text}")

def print_info(text):
    print(f"{Colors.BLUE}→{Colors.END} {text}")

def print_warning(text):
    print(f"{Colors.YELLOW}⚠{Colors.END} {text}")

def test_ollama_server(ollama_url=None):
    if ollama_url is None:
        port = os.environ.get('OLLAMA_API_PORT', '11434')
        ollama_url = f"http://localhost:{port}"
    """Test 1: Check if Ollama server is running"""
    print_header("TEST 1: Ollama Server Connection")

    try:
        response = requests.get(ollama_url, timeout=5)
        if response.status_code == 200:
            print_success("Ollama server is running")
            return True
        else:
            print_error(f"Ollama server returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print_error(f"Cannot connect to Ollama at {ollama_url}")
        print_info("Start Ollama with: ollama serve")
        return False
    except Exception as e:
        print_error(f"Connection error: {e}")
        return False

def test_model_availability(ollama_url="http://localhost:11434", model=None):
    """Test 2: Check if configured model is installed"""
    if model is None:
        model = os.environ.get('OLLAMA_MODEL', 'qwen2.5:72b-instruct-q4_K_M')
    print_header("TEST 2: Model Availability")

    try:
        response = requests.get(f"{ollama_url}/api/tags", timeout=5)
        response.raise_for_status()
        data = response.json()

        available_models = [m['name'] for m in data.get('models', [])]
        print_info(f"Available models: {', '.join(available_models)}")

        # Check for model
        model_found = False
        for available in available_models:
            if available == model or available.startswith(f"{model}:"):
                model_found = True
                print_success(f"Model '{model}' is installed")

                # Get model details
                for m in data.get('models', []):
                    if m['name'] == available:
                        size_gb = m.get('size', 0) / (1024**3)
                        print_info(f"  Size: {size_gb:.1f} GB")
                        modified = m.get('modified_at', 'unknown')
                        print_info(f"  Modified: {modified}")
                break

        if not model_found:
            print_error(f"Model '{model}' not found")
            print_info(f"Install with: ollama pull {model}")
            return False

        return True

    except Exception as e:
        print_error(f"Error checking models: {e}")
        return False

def test_gpu_availability():
    """Test 3: Check GPU availability"""
    print_header("TEST 3: GPU Availability")

    try:
        import subprocess
        result = subprocess.run(
            ['nvidia-smi', '--query-gpu=index,name,memory.total,memory.free', '--format=csv,noheader'],
            capture_output=True,
            text=True,
            timeout=3
        )

        if result.returncode == 0 and result.stdout:
            print_success("NVIDIA GPU(s) detected:")
            for line in result.stdout.strip().split('\n'):
                print(f"  {line}")

            # Check CUDA device 1 specifically
            lines = result.stdout.strip().split('\n')
            if len(lines) >= 2:
                print_info("CUDA device 1 (RTX A6000) available for Ollama")

            return True
        else:
            print_warning("nvidia-smi failed. Running on CPU.")
            return False

    except FileNotFoundError:
        print_warning("nvidia-smi not found. GPU may not be available.")
        print_info("CPU inference will be significantly slower (~10x)")
        return False
    except Exception as e:
        print_warning(f"Could not check GPU: {e}")
        return False

def test_scoring_inference(ollama_url="http://localhost:11434", model=None):
    if model is None:
        model = os.environ.get('OLLAMA_MODEL', 'qwen2.5:72b-instruct-q4_K_M')
    """Test 4: Run sample scoring inference"""
    print_header("TEST 4: Sample Scoring Inference")

    # Sample ASP education paper (high score expected)
    test_cases = [
        {
            "title": "Development of an Antimicrobial Stewardship Fellowship Program",
            "abstract": "We describe the development and implementation of a structured fellowship program for antimicrobial stewardship training. The curriculum includes formal didactics, mentored research, and competency-based assessments.",
            "expected_score": "8-10"
        },
        {
            "title": "Impact of Antibiotic Restriction on Hospital Costs",
            "abstract": "This study evaluated the cost savings associated with implementing formulary restrictions on broad-spectrum antibiotics in a tertiary care hospital over 12 months.",
            "expected_score": "1-4"
        }
    ]

    system_prompt = (
        "You are an expert medical librarian specializing in Antimicrobial Stewardship education. "
        "Rate papers on relevance to ASP TRAINING/EDUCATION (0-10):\n\n"
        "10: Core ASP education (curriculum design, teaching methods, training programs)\n"
        "8-9: Strong training focus (competency assessment, educational interventions)\n"
        "6-7: Mixed clinical/educational (implementation with training component)\n"
        "4-5: Minimal education (brief mention of training in QI project)\n"
        "1-3: Tangential (general ASP topics, no educational focus)\n"
        "0: Not relevant\n\n"
        "Respond with ONLY the numeric score (0-10). No explanation."
    )

    all_passed = True

    for i, test_case in enumerate(test_cases, 1):
        print_info(f"\nTest case {i}:")
        print(f"  Title: {test_case['title'][:60]}...")
        print(f"  Expected: {test_case['expected_score']}")

        user_prompt = f"Title: {test_case['title']}\n\nAbstract: {test_case['abstract']}"

        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "stream": False,
            "options": {
                "temperature": 0.0,
                "num_predict": 128
            }
        }

        start_time = time.time()

        try:
            response = requests.post(f"{ollama_url}/api/chat", json=payload, timeout=60)
            response.raise_for_status()
            result = response.json()
            answer = result.get('message', {}).get('content', '').strip()

            elapsed = time.time() - start_time

            # Try to extract score
            import re
            match = re.search(r'\b([0-9]|10)(?:\.\d+)?\b', answer)
            if match:
                score = float(match.group(0))
                print_success(f"Score: {score}/10 (inference time: {elapsed:.1f}s)")

                # Check if score is in expected range
                expected_range = test_case['expected_score'].split('-')
                low = int(expected_range[0])
                high = int(expected_range[1])

                if low <= score <= high:
                    print_success(f"  Score within expected range ✓")
                else:
                    print_warning(f"  Score outside expected range (may need prompt tuning)")
                    all_passed = False
            else:
                print_error(f"Could not parse score from: '{answer}'")
                all_passed = False

        except requests.exceptions.Timeout:
            print_error("Request timed out (>60s)")
            print_info("This may indicate the model is too slow on your hardware")
            all_passed = False
        except Exception as e:
            print_error(f"Inference failed: {e}")
            all_passed = False

    return all_passed

def main():
    """Run all tests"""
    model = os.environ.get('OLLAMA_MODEL', 'qwen2.5:72b-instruct-q4_K_M')
    print(f"\n{Colors.BOLD}Ollama {model} Setup Test{Colors.END}")
    print("Testing ASP Literature Miner AI configuration\n")

    results = {}

    # Test 1: Server connection
    results['server'] = test_ollama_server()

    if not results['server']:
        print_error("\nCannot proceed without Ollama server")
        print_info("Install Ollama: https://ollama.ai/download")
        sys.exit(1)

    # Test 2: Model availability
    results['model'] = test_model_availability()

    if not results['model']:
        model = os.environ.get('OLLAMA_MODEL', 'qwen2.5:72b-instruct-q4_K_M')
        print_error(f"\nCannot proceed without {model} model")
        print_info(f"Run: ollama pull {model}")
        sys.exit(1)

    # Test 3: GPU
    results['gpu'] = test_gpu_availability()

    # Test 4: Inference
    results['inference'] = test_scoring_inference()

    # Summary
    print_header("TEST SUMMARY")

    for test_name, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        color = Colors.GREEN if passed else Colors.RED
        print(f"{color}{status}{Colors.END} - {test_name.title()}")

    all_passed = all(results.values())

    if all_passed:
        print_success("\nAll tests passed! Ready to run asp_literature_miner.py")
        print_info("\nRecommended command:")
        model = os.environ.get('OLLAMA_MODEL', 'qwen2.5:72b-instruct-q4_K_M')
        print(f"  python asp_literature_miner.py --step filter --model {model} --score-threshold 7.0")
    else:
        print_warning("\nSome tests failed. Please fix issues before running the literature miner.")

    return 0 if all_passed else 1

if __name__ == '__main__':
    sys.exit(main())
