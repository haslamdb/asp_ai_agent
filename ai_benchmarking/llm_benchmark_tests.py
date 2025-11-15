#!/usr/bin/env python3
"""
LLM Benchmark Test Suite
Comprehensive tests for comparing different language models on coding and reasoning tasks
"""

import subprocess
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

# Test categories and prompts
TESTS = {
    "code_generation": [
        {
            "name": "python_data_processing",
            "prompt": """Write a Python function that reads a CSV file with columns 'sample_id', 'reads_count', 'gc_content'
and filters rows where reads_count > 1000000 and gc_content is between 40 and 60.
Return a pandas DataFrame sorted by reads_count descending. Include error handling.""",
            "criteria": ["correctness", "error handling", "efficiency", "code style"]
        },
        {
            "name": "bash_file_processing",
            "prompt": """Write a bash script that:
1. Finds all .fastq.gz files in a directory tree
2. For each file, checks if a corresponding .md5 file exists
3. If md5 exists, verifies the checksum
4. Logs results to a file with timestamps
5. Returns exit code 1 if any checksum fails""",
            "criteria": ["correctness", "robustness", "logging", "error handling"]
        },
        {
            "name": "api_client",
            "prompt": """Create a Python class that interacts with NCBI's E-utilities API to:
1. Search for BioProject records by keyword
2. Fetch detailed metadata for a given BioProject ID
3. Handle rate limiting (max 3 requests/second)
4. Implement retry logic with exponential backoff
5. Include proper error handling and logging
Use requests library and follow best practices.""",
            "criteria": ["API design", "error handling", "rate limiting", "code organization"]
        }
    ],

    "debugging": [
        {
            "name": "identify_bug",
            "prompt": """Find and fix the bugs in this code:

```python
def process_samples(file_path):
    samples = {}
    with open(file_path) as f:
        for line in f:
            id, count = line.split(',')
            samples[id] = int(count)

    avg = sum(samples.values()) / len(samples)

    filtered = {k: v for k, v in samples if v > avg}
    return filtered
```

Explain each bug and provide the corrected version.""",
            "criteria": ["bug identification", "explanation quality", "fix correctness"]
        }
    ],

    "code_review": [
        {
            "name": "review_security",
            "prompt": """Review this code for security issues and best practices:

```python
import os
import subprocess

def upload_to_server(filename, server):
    password = os.getenv('FTP_PASSWORD')
    cmd = f"ftp -u {filename} ftp://{server}/uploads/"
    subprocess.call(cmd, shell=True)

    with open(filename, 'r') as f:
        data = eval(f.read())

    return data
```

List all issues and provide improved version.""",
            "criteria": ["security awareness", "issue identification", "recommendations"]
        }
    ],

    "refactoring": [
        {
            "name": "improve_code_quality",
            "prompt": """Refactor this code to improve readability, maintainability, and efficiency:

```python
def process(data):
    r = []
    for i in range(len(data)):
        if data[i][1] > 1000000:
            if data[i][2] >= 40 and data[i][2] <= 60:
                r.append(data[i])
    r.sort(key=lambda x: x[1])
    r.reverse()
    return r
```

Explain your improvements.""",
            "criteria": ["readability", "pythonic style", "performance", "explanation"]
        }
    ],

    "algorithm_design": [
        {
            "name": "efficient_deduplication",
            "prompt": """Design an efficient algorithm to deduplicate DNA sequence reads from multiple FASTQ files.
Requirements:
- Handle files too large to fit in memory
- Preserve order of first occurrence
- Track duplicate statistics
- Process ~100GB of data efficiently

Provide pseudocode and explain time/space complexity.""",
            "criteria": ["algorithm efficiency", "memory management", "scalability", "explanation"]
        }
    ],

    "reasoning": [
        {
            "name": "system_design",
            "prompt": """Design a system for automated SRA (Sequence Read Archive) submissions that:
1. Validates metadata against SRA requirements
2. Uploads large files (100GB+) with resume capability
3. Handles submission status checking
4. Retries failed operations
5. Sends notifications on completion/failure

Describe the architecture, key components, and data flow.""",
            "criteria": ["design quality", "completeness", "practicality", "error handling"]
        },
        {
            "name": "troubleshooting",
            "prompt": """A bioinformatics pipeline is failing with 'Out of Memory' errors when processing samples larger than 50GB.
The system has 128GB RAM. The pipeline:
1. Loads entire FASTQ file into memory
2. Performs quality filtering
3. Runs alignment with BWA
4. Generates statistics

What could be causing the issue? Propose solutions with tradeoffs.""",
            "criteria": ["problem analysis", "solution quality", "tradeoff discussion"]
        },
        {
            "name": "medical_reasoning_cicu",
            "prompt": """You are an Antimicrobial Stewardship (ASP) fellow reviewing CICU antibiotic usage data. The data shows:
- 850 DOT (days of therapy) per 1000 patient days for meropenem+vancomycin combination
- Average duration: 8.5 days (vs. 3-5 days recommended)
- 92% of patients with negative cultures at 48 hours continue antibiotics
- Annual excess medication cost: $380,000

The CICU leadership cites these concerns:
"These are critically ill cardiac patients - we can't take risks"
"Our patients differ from general PICU"
"Weekly attending rotation disrupts consistency"

Design a comprehensive intervention to reduce inappropriate antibiotic use that addresses:
1. Data-driven approach to demonstrate safety
2. Behavioral change strategies for prescribers
3. Implementation plan with measurable outcomes
4. Methods to address hierarchy and fear-based prescribing
5. Sustainability mechanisms

Include specific metrics, timeline, and how you would handle resistance from senior attendings.""",
            "criteria": ["clinical knowledge", "behavior change strategy", "implementation science", "stakeholder engagement", "data-driven approach"]
        }
    ],

    "documentation": [
        {
            "name": "write_readme",
            "prompt": """Write a comprehensive README.md for a Python package that submits sequencing data to NCBI SRA.
Include: installation, configuration, usage examples, API reference, troubleshooting, and contribution guidelines.""",
            "criteria": ["completeness", "clarity", "organization", "examples"]
        }
    ],

    "testing": [
        {
            "name": "write_unit_tests",
            "prompt": """Write comprehensive pytest unit tests for this function:

```python
def calculate_gc_content(sequence: str) -> float:
    '''Calculate GC content percentage of a DNA sequence.'''
    if not sequence:
        raise ValueError("Empty sequence")
    gc_count = sequence.upper().count('G') + sequence.upper().count('C')
    return (gc_count / len(sequence)) * 100
```

Include edge cases and error conditions.""",
            "criteria": ["test coverage", "edge cases", "test organization"]
        }
    ]
}


class LLMBenchmark:
    """Benchmark different LLM models using Ollama"""

    def __init__(self, models: List[str], output_dir: str = "llm_benchmark_results"):
        self.models = models
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.results = {}

    def run_prompt(self, model: str, prompt: str, timeout: int = None) -> Tuple[str, float]:
        """Run a single prompt on a model and return response + time taken"""
        start = time.time()
        try:
            result = subprocess.run(
                ["ollama", "run", model, prompt],
                capture_output=True,
                text=True,
                timeout=timeout  # None means no timeout
            )
            elapsed = time.time() - start
            return result.stdout.strip(), elapsed
        except subprocess.TimeoutExpired:
            return "[TIMEOUT]", timeout
        except Exception as e:
            return f"[ERROR: {str(e)}]", 0

    def unload_model(self, model: str):
        """Unload a model from VRAM"""
        try:
            subprocess.run(
                ["ollama", "stop", model],
                capture_output=True,
                timeout=30
            )
        except Exception as e:
            print(f"    Warning: Failed to unload {model}: {e}")

    def run_test_category(self, category: str, tests: List[Dict]) -> Dict:
        """Run all tests in a category across all models"""
        print(f"\n{'='*80}")
        print(f"Testing Category: {category.upper().replace('_', ' ')}")
        print(f"{'='*80}\n")

        category_results = {}

        for test_idx, test in enumerate(tests, 1):
            test_name = test['name']
            prompt = test['prompt']

            print(f"  Test {test_idx}/{len(tests)}: {test_name}")
            print(f"  Criteria: {', '.join(test['criteria'])}")
            print()

            test_results = {}

            for model in self.models:
                print(f"    Running on {model}...", end=" ", flush=True)
                response, elapsed = self.run_prompt(model, prompt)

                test_results[model] = {
                    "response": response,
                    "time_seconds": elapsed,
                    "timestamp": datetime.now().isoformat()
                }

                print(f"✓ ({elapsed:.1f}s)")

                # Unload model from VRAM before testing next model
                self.unload_model(model)

            category_results[test_name] = {
                "prompt": prompt,
                "criteria": test['criteria'],
                "results": test_results
            }
            print()

        return category_results

    def run_all_tests(self):
        """Run all test categories"""
        print(f"\n{'#'*80}")
        print(f"# LLM Benchmark Suite")
        print(f"# Models: {', '.join(self.models)}")
        print(f"# Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'#'*80}")

        all_results = {
            "metadata": {
                "models": self.models,
                "start_time": datetime.now().isoformat(),
                "test_categories": list(TESTS.keys())
            },
            "results": {}
        }

        for category, tests in TESTS.items():
            category_results = self.run_test_category(category, tests)
            all_results["results"][category] = category_results

        all_results["metadata"]["end_time"] = datetime.now().isoformat()

        # Save results
        output_file = self.output_dir / f"benchmark_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w') as f:
            json.dump(all_results, f, indent=2)

        print(f"\n{'='*80}")
        print(f"Benchmark complete! Results saved to: {output_file}")
        print(f"{'='*80}\n")

        # Generate summary
        self.generate_summary(all_results)

        return all_results

    def generate_summary(self, results: Dict):
        """Generate a summary report"""
        print("\n" + "="*80)
        print("SUMMARY")
        print("="*80 + "\n")

        # Calculate average response times per model
        model_times = {model: [] for model in self.models}

        for category_data in results["results"].values():
            for test_data in category_data.values():
                for model, result in test_data["results"].items():
                    # Exclude timeouts and errors (response starts with "[")
                    if not result["response"].startswith("["):
                        model_times[model].append(result["time_seconds"])

        print("Average Response Times:")
        for model in self.models:
            if model_times[model]:
                avg_time = sum(model_times[model]) / len(model_times[model])
                print(f"  {model:30s}: {avg_time:6.2f}s")

        print(f"\nTotal tests per model: {sum(len(tests) for tests in TESTS.values())}")
        print(f"Categories tested: {len(TESTS)}")


def compare_responses(result_file: str, test_name: str):
    """Load results and display side-by-side comparison for a specific test"""
    with open(result_file, 'r') as f:
        data = json.load(f)

    # Find the test
    for category, tests in data["results"].items():
        if test_name in tests:
            test_data = tests[test_name]
            print(f"\n{'='*80}")
            print(f"Test: {test_name} (Category: {category})")
            print(f"{'='*80}\n")
            print(f"Prompt:\n{test_data['prompt']}\n")
            print(f"Criteria: {', '.join(test_data['criteria'])}\n")

            for model, result in test_data["results"].items():
                print(f"\n{'-'*80}")
                print(f"Model: {model} ({result['time_seconds']:.1f}s)")
                print(f"{'-'*80}")
                print(result["response"][:2000])  # Limit output length
                if len(result["response"]) > 2000:
                    print("\n[... truncated ...]")

            return

    print(f"Test '{test_name}' not found in results")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="LLM Benchmark Suite")
    parser.add_argument("--models", nargs="+",
                       default=["gemma2:27b", "qwen2.5:72b-instruct-q4_K_M", "llama3.1:70b", "deepseek-r1:70b", "openbiollm:70b"],
                       help="List of models to benchmark")
    parser.add_argument("--output-dir", default="llm_benchmark_results",
                       help="Output directory for results")
    parser.add_argument("--compare", help="Compare responses from a result file for a specific test")
    parser.add_argument("--test-name", help="Test name to compare (use with --compare)")
    parser.add_argument("--categories", nargs="+", choices=list(TESTS.keys()),
                       help="Run only specific categories")

    args = parser.parse_args()

    if args.compare:
        if not args.test_name:
            print("Error: --test-name required with --compare")
        else:
            compare_responses(args.compare, args.test_name)
    else:
        # Filter tests if categories specified
        if args.categories:
            filtered_tests = {k: v for k, v in TESTS.items() if k in args.categories}
            TESTS.clear()
            TESTS.update(filtered_tests)

        benchmark = LLMBenchmark(args.models, args.output_dir)
        benchmark.run_all_tests()
