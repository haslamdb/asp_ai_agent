#!/bin/bash
# Quick LLM comparison script - run a single prompt on multiple models

PROMPT="${1:-Write a Python function to calculate GC content of a DNA sequence with error handling}"

MODELS=(
    "gemma2:27b"
    "qwen2.5:72b-instruct-q4_K_M"
    "llama3.1:70b"
    "deepseek-r1:70b"
    "deepseek-r1:70b-0528"
)

echo "=========================================="
echo "Quick LLM Test"
echo "=========================================="
echo ""
echo "Prompt: $PROMPT"
echo ""
echo "Testing models..."
echo ""

for model in "${MODELS[@]}"; do
    # Check if model exists
    if ! ollama list | grep -q "^$model"; then
        echo "⊘ $model - NOT INSTALLED (skipping)"
        continue
    fi

    echo "=========================================="
    echo "Model: $model"
    echo "=========================================="
    echo ""

    start=$(date +%s)
    ollama run "$model" "$PROMPT"
    end=$(date +%s)
    elapsed=$((end - start))

    echo ""
    echo "Time: ${elapsed}s"
    echo ""
done

echo "=========================================="
echo "Test Complete!"
echo "=========================================="
