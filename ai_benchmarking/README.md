# LLM Benchmarks

Comprehensive testing framework for comparing language models on coding and reasoning tasks.

## 📁 Project Structure

```
~/projects/llm_benchmarks/
├── README.md                      # This file
├── LLM_BENCHMARKS.md             # Full documentation
├── llm_benchmark_tests.py        # Complete benchmark suite
├── quick_llm_test.sh             # Quick single-prompt tester
├── demo_model_comparison.sh      # Interactive demo
└── llm_benchmark_results/        # Output directory for results
```

## 🚀 Quick Start

```bash
cd ~/projects/llm_benchmarks

# 1. Interactive demo - compare models on a real problem
./demo_model_comparison.sh

# 2. Quick test with custom prompt
./quick_llm_test.sh "Write a Python function to calculate GC content"

# 3. Full benchmark suite (comprehensive, ~30-60 min)
python llm_benchmark_tests.py

# 4. Read detailed documentation
cat LLM_BENCHMARKS.md
```

## 📊 Available Models

Currently installed on your system:

| Model | Size | Best For |
|-------|------|----------|
| `gemma2:27b` | 15 GB | Fast prototyping, quick tasks |
| `qwen2.5:72b-instruct-q4_K_M` | 47 GB | Strong instruction-following |
| `llama3.1:70b` | 42 GB | Well-rounded coding |
| `deepseek-r1:70b` | 42 GB | Complex reasoning, 131K context |

## 🎯 Use Cases

### For Coding
```bash
./quick_llm_test.sh "Refactor this function to use pandas instead of loops"
```

### For Debugging
```bash
./quick_llm_test.sh "Why is my Aspera upload getting permission denied errors?"
```

### Full Comparison
```bash
# Test all models across multiple categories
python llm_benchmark_tests.py

# Test specific categories
python llm_benchmark_tests.py --categories code_generation debugging
```

## 📖 Documentation

See **LLM_BENCHMARKS.md** for:
- Detailed test descriptions
- Model comparison guide
- GPU memory management
- Advanced usage examples
- Tips for best results

## 💾 Results

All benchmark results are saved as timestamped JSON files in `llm_benchmark_results/`:
```bash
llm_benchmark_results/benchmark_20251114_150000.json
```

Compare results:
```bash
python llm_benchmark_tests.py --compare llm_benchmark_results/benchmark_*.json --test-name python_data_processing
```

## 🔧 GPU Setup

Your hardware:
- RTX A6000: 48 GB VRAM
- RTX A5000: 24 GB VRAM
- **Total: 72 GB VRAM**

All your models fit comfortably. Monitor with:
```bash
watch -n 1 nvidia-smi
```

## 🎮 Next Steps

1. ✅ Run `./demo_model_comparison.sh` to see models in action
2. ✅ Try `./quick_llm_test.sh` with your own coding questions
3. ✅ Run full benchmark when you have time
4. ✅ Review results and pick your favorite model(s)
5. ✅ Create custom tests for your specific workflows

---

**Ready to start?** Run `./demo_model_comparison.sh` now!
