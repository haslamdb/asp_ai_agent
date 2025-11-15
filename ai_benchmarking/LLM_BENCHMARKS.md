# LLM Benchmark Suite

Comprehensive testing framework for comparing language models on coding and reasoning tasks.

## Available Models

Currently installed:
- **gemma2:27b** (15 GB) - Google's Gemma 2 27B
- **qwen2.5:72b-instruct-q4_K_M** (47 GB) - Alibaba's Qwen 2.5 72B
- **llama3.1:70b** (42 GB) - Meta's Llama 3.1 70B
- **deepseek-r1:70b** (42 GB) - DeepSeek R1 70B with reasoning capability

## Quick Start

### Run a Quick Test (Single Prompt)

```bash
# Test all models with a default coding prompt
./quick_llm_test.sh

# Custom prompt
./quick_llm_test.sh "Write a Python function to parse FASTQ files and calculate quality scores"
```

### Run Full Benchmark Suite

```bash
# Test all models on all categories
python llm_benchmark_tests.py

# Test specific models only
python llm_benchmark_tests.py --models gemma2:27b deepseek-r1:70b

# Test specific categories only
python llm_benchmark_tests.py --categories code_generation debugging

# Compare results from a previous run
python llm_benchmark_tests.py --compare llm_benchmark_results/benchmark_20251114_150000.json --test-name python_data_processing
```

## Test Categories

### 1. **Code Generation** (3 tests)
- Python data processing with pandas
- Bash script for file processing with checksums
- API client with rate limiting and retry logic

**Best for:** Evaluating practical coding ability, library usage, error handling

### 2. **Debugging** (1 test)
- Identify and fix bugs in sample code

**Best for:** Code comprehension, problem-solving

### 3. **Code Review** (1 test)
- Security audit and best practices review

**Best for:** Security awareness, code quality understanding

### 4. **Refactoring** (1 test)
- Improve code readability and efficiency

**Best for:** Code quality, Pythonic style, optimization

### 5. **Algorithm Design** (1 test)
- Design efficient deduplication algorithm for large-scale data

**Best for:** Algorithmic thinking, scalability, complexity analysis

### 6. **Reasoning** (2 tests)
- System architecture design
- Troubleshooting complex issues

**Best for:** High-level thinking, practical problem-solving

### 7. **Documentation** (1 test)
- Write comprehensive README

**Best for:** Communication clarity, completeness

### 8. **Testing** (1 test)
- Write unit tests with edge cases

**Best for:** Test-driven development, edge case thinking

## Understanding Results

### Result Files

Benchmark results are saved as JSON in `llm_benchmark_results/`:
```
llm_benchmark_results/
├── benchmark_20251114_150000.json
└── benchmark_20251114_160000.json
```

Each file contains:
- Metadata (models tested, timestamps)
- Full responses for each test
- Response times
- Test prompts and evaluation criteria

### Metrics to Consider

1. **Response Time** - Speed (but faster ≠ always better!)
2. **Code Quality** - Correctness, style, best practices
3. **Error Handling** - Robustness, edge cases
4. **Completeness** - Does it fully answer the prompt?
5. **Explanation Quality** - Can it explain the code/reasoning?
6. **Security Awareness** - Does it avoid vulnerabilities?

### Manual Evaluation

The benchmark provides quantitative data (response times) but requires manual evaluation of quality:

```bash
# View side-by-side comparison for a specific test
python llm_benchmark_tests.py --compare llm_benchmark_results/benchmark_20251114_150000.json --test-name python_data_processing
```

## Model Comparison Guide

### When to Use Each Model

#### **Gemma2:27b** (15 GB)
- ✅ Fastest responses
- ✅ Lowest VRAM usage
- ✅ Good for quick prototyping
- ⚠️ May struggle with complex reasoning

#### **Qwen2.5:72b-instruct-q4_K_M** (47 GB)
- ✅ Strong instruction following
- ✅ Good multilingual support
- ✅ Balanced speed/quality
- ⚠️ Moderate VRAM usage

#### **Llama3.1:70b** (42 GB)
- ✅ Well-rounded general purpose
- ✅ Strong coding abilities
- ✅ Good reasoning
- ⚠️ Can be verbose

#### **DeepSeek-R1:70b** (42 GB)
- ✅ **Explicit reasoning** (shows thought process)
- ✅ Strong at complex problem-solving
- ✅ Excellent for debugging/analysis
- ✅ 131K context length (2x others!)
- ⚠️ May be slower due to reasoning steps

## Example Workflows

### For Coding Tasks

1. **Quick prototype/simple tasks**: `gemma2:27b`
2. **Production code with error handling**: `qwen2.5:72b` or `llama3.1:70b`
3. **Complex debugging/system design**: `deepseek-r1:70b`

### For Your Use Cases

**Bioinformatics pipeline code:**
```bash
ollama run qwen2.5:72b-instruct-q4_K_M "Write a Python script to process SRA metadata and validate against NCBI requirements"
```

**Debugging issues:**
```bash
ollama run deepseek-r1:70b "This Aspera upload is failing with permission errors. The upload destination is [...]. Here's the error: [...]. What could be wrong?"
```

**AI Training Module Development:**
```bash
ollama run llama3.1:70b "Design an interactive training system for teaching bioinformatics workflows with AI assistance"
```

## GPU Memory Management

Your setup:
- RTX A6000: 48 GB VRAM
- RTX A5000: 24 GB VRAM
- Total: 72 GB

### Model Loading Strategy

Ollama will automatically use available GPUs. To control which GPU:

```bash
# Use specific GPU
CUDA_VISIBLE_DEVICES=0 ollama run gemma2:27b  # Use A6000
CUDA_VISIBLE_DEVICES=1 ollama run gemma2:27b  # Use A5000

# Monitor GPU usage
watch -n 1 nvidia-smi
```

### Concurrent Models

You can run multiple models simultaneously:
```bash
# Terminal 1: Use A6000
CUDA_VISIBLE_DEVICES=0 ollama run deepseek-r1:70b

# Terminal 2: Use A5000
CUDA_VISIBLE_DEVICES=1 ollama run gemma2:27b
```

## Tips for Best Results

1. **Be Specific**: More detailed prompts = better results
2. **Provide Context**: Include relevant code, error messages, requirements
3. **Iterate**: Use responses as starting points, refine with follow-ups
4. **Compare Models**: Different models excel at different tasks
5. **Use Reasoning Models for Hard Problems**: DeepSeek-R1's "thinking" process helps with complex issues

## Advanced: Custom Tests

Add your own tests to `llm_benchmark_tests.py`:

```python
TESTS["your_category"] = [
    {
        "name": "test_name",
        "prompt": "Your prompt here...",
        "criteria": ["criterion1", "criterion2"]
    }
]
```

## Monitoring & Management

```bash
# View running models
ollama ps

# Stop a running model (frees VRAM)
# Press Ctrl+D in the ollama session

# List all models
ollama list

# Remove a model
ollama rm model-name

# Check model details
ollama show model-name
```

## Next Steps

1. Run quick test to get familiar with each model
2. Run full benchmark (takes ~30-60 min depending on models)
3. Review results and identify which model suits your needs
4. Integrate best model(s) into your workflow
5. Create custom tests for your specific use cases

## Results Tracking

Keep a log of your findings:

```bash
# After each benchmark
echo "$(date): Tested models on coding tasks" >> benchmark_log.txt
echo "Winner: deepseek-r1:70b for complex debugging" >> benchmark_log.txt
```

---

**Need help?** Check `ollama --help` or visit https://ollama.ai/library
