#!/bin/bash
# Demo: Quick model comparison on a real coding task

echo "=========================================="
echo "LLM Model Comparison Demo"
echo "=========================================="
echo ""
echo "Testing coding task: Fix the SRA upload permission issue"
echo ""

PROMPT="I'm uploading files to NCBI SRA using this command:

ollama pull deepseek-v3

It's failing with: 'Error: open /home/david/models/blobs/sha256-xxx-partial-0: permission denied'

The Ollama service runs as user 'ollama', but the files are in /home/david/models/.
The OLLAMA_MODELS env var is set to /home/david/models.

What's the issue and how do I fix it? Provide the exact commands."

# Test with 3 models for comparison
MODELS=("gemma2:27b" "llama3.1:70b" "deepseek-r1:70b")

for model in "${MODELS[@]}"; do
    if ! ollama list | grep -q "^$model"; then
        echo "⊘ Skipping $model (not installed)"
        continue
    fi

    echo ""
    echo "=========================================="
    echo "Model: $model"
    echo "=========================================="
    echo ""

    start=$(date +%s)
    response=$(timeout 180 ollama run "$model" "$PROMPT" 2>&1)
    end=$(date +%s)
    elapsed=$((end - start))

    echo "$response"
    echo ""
    echo "⏱ Response time: ${elapsed}s"
    echo ""
    echo "Press Enter to continue to next model..."
    read
done

echo ""
echo "=========================================="
echo "Comparison Complete!"
echo "=========================================="
echo ""
echo "Which model gave the best answer?"
echo "- Gemma: Fastest but potentially less detailed"
echo "- Llama: Balanced speed and quality"
echo "- DeepSeek-R1: Shows reasoning process, may be most thorough"
