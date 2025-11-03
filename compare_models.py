#!/usr/bin/env python3
"""
Compare different Ollama models for ASP trainee response evaluation
"""
import os
import requests
import json
import time
from datetime import datetime
import subprocess

def get_gpu_info():
    """Get current GPU usage information"""
    try:
        result = subprocess.run(['nvidia-smi', '--query-gpu=index,name,memory.used,memory.total,utilization.gpu,temperature.gpu', 
                                '--format=csv,noheader,nounits'], 
                               capture_output=True, text=True)
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            gpus = []
            for line in lines:
                parts = line.split(', ')
                gpus.append({
                    'index': int(parts[0]),
                    'name': parts[1],
                    'memory_used': int(parts[2]),
                    'memory_total': int(parts[3]),
                    'utilization': int(parts[4]),
                    'temperature': int(parts[5])
                })
            return gpus
    except Exception as e:
        return None
    
def get_ollama_gpu_processes():
    """Check which processes are using GPUs"""
    try:
        result = subprocess.run(['nvidia-smi', '--query-compute-apps=pid,process_name,used_memory', 
                                '--format=csv,noheader,nounits'],
                               capture_output=True, text=True)
        if result.returncode == 0 and result.stdout.strip():
            processes = []
            for line in result.stdout.strip().split('\n'):
                if line:
                    parts = line.split(', ')
                    processes.append({
                        'pid': int(parts[0]),
                        'name': parts[1],
                        'memory': int(parts[2])
                    })
            return processes
    except Exception:
        pass
    return []

def test_model(model_name, trainee_response, scenario):
    """Test a specific model with a trainee response"""
    port = os.environ.get('OLLAMA_API_PORT', '11434')
    url = f"http://localhost:{port}/api/generate"
    
    prompt = f"""
You are evaluating a trainee's response to an antimicrobial stewardship scenario.

SCENARIO:
{scenario}

TRAINEE'S RESPONSE:
{trainee_response}

Please evaluate this response on:
1. Clinical accuracy (0-10)
2. Understanding of stewardship principles (0-10)
3. Communication effectiveness (0-10)
4. Overall score (0-10)

Provide brief reasoning for each score.
"""
    
    system_prompt = "You are an expert in antimicrobial stewardship education."
    full_prompt = f"{system_prompt}\n\n{prompt}"
    
    payload = {
        "model": model_name,
        "prompt": full_prompt,
        "stream": False
    }
    
    print(f"\n{'='*60}")
    print(f"Testing model: {model_name}")
    print(f"{'='*60}")
    
    # Show GPU status before model inference
    gpu_info_before = get_gpu_info()
    if gpu_info_before:
        print("\nGPU Status BEFORE inference:")
        for gpu in gpu_info_before:
            print(f"  GPU {gpu['index']} ({gpu['name']}): "
                  f"{gpu['memory_used']}/{gpu['memory_total']} MB, "
                  f"{gpu['utilization']}% util, {gpu['temperature']}°C")
    
    start_time = time.time()
    try:
        response = requests.post(url, json=payload, timeout=120)
        response.raise_for_status()
        elapsed = time.time() - start_time
        
        # Show GPU status after model inference
        gpu_info_after = get_gpu_info()
        if gpu_info_after:
            print("\nGPU Status AFTER inference:")
            for gpu in gpu_info_after:
                print(f"  GPU {gpu['index']} ({gpu['name']}): "
                      f"{gpu['memory_used']}/{gpu['memory_total']} MB, "
                      f"{gpu['utilization']}% util, {gpu['temperature']}°C")
            
            # Show memory delta
            if gpu_info_before:
                print("\nGPU Memory Change:")
                for i, (before, after) in enumerate(zip(gpu_info_before, gpu_info_after)):
                    delta = after['memory_used'] - before['memory_used']
                    if delta != 0:
                        print(f"  GPU {i}: {delta:+} MB")
        
        # Check for GPU processes
        processes = get_ollama_gpu_processes()
        if processes:
            print("\nGPU Processes:")
            for proc in processes:
                if 'ollama' in proc['name'].lower():
                    print(f"  PID {proc['pid']}: {proc['name']} - {proc['memory']} MB")
        
        result = response.json()
        print(f"\nResponse time: {elapsed:.2f} seconds")
        print("\nEvaluation:")
        print(result.get('response', 'No response'))
        
        return result.get('response', 'No response'), elapsed
    except Exception as e:
        print(f"Error: {e}")
        return None, 0

def main():
    # Show initial GPU status
    print("="*60)
    print("INITIAL GPU STATUS")
    print("="*60)
    gpus = get_gpu_info()
    if gpus:
        for gpu in gpus:
            print(f"GPU {gpu['index']} ({gpu['name']}): "
                  f"{gpu['memory_used']}/{gpu['memory_total']} MB, "
                  f"{gpu['utilization']}% util, {gpu['temperature']}°C")
    else:
        print("No GPU information available")
    
    # Check CUDA environment variable
    cuda_visible = os.environ.get('CUDA_VISIBLE_DEVICES')
    if cuda_visible:
        print(f"\nCUDA_VISIBLE_DEVICES: {cuda_visible}")
    else:
        print("\nCUDA_VISIBLE_DEVICES: Not set (all GPUs visible)")
    
    # Sample scenario and trainee response
    scenario = """
    A 6-year-old patient presents with suspected community-acquired pneumonia. 
    They have a penicillin allergy (rash only, not anaphylaxis). 
    Current antibiotic: IV ceftriaxone 2g daily for 3 days.
    Clinical improvement noted, afebrile for 24 hours.
    Question: What antibiotic stewardship interventions would you recommend?
    """
    
    trainee_response = """
    I would recommend switching from IV to oral antibiotics since the patient 
    is clinically improving and afebrile. We could use oral amoxicillin-clavulanate 
    or a fluoroquinolone like levofloxacin. This IV to oral switch would reduce 
    costs and allow earlier discharge. I would also review the culture results 
    if available to ensure we're using the narrowest spectrum antibiotic.
    """
    
    models = [
        'gemma2:27b', 
        'llama3.1:70b',
        'qwen2.5:72b-instruct-q4_K_M'
    ]
    
    results = {}
    for model in models:
        evaluation, time_taken = test_model(model, trainee_response, scenario)
        if evaluation:
            results[model] = {
                'evaluation': evaluation,
                'time': time_taken
            }
    
    # Summary
    print(f"\n{'='*60}")
    print("COMPARISON SUMMARY")
    print(f"{'='*60}")
    for model, data in results.items():
        print(f"\n{model}:")
        print(f"  Response time: {data['time']:.2f}s")
        print(f"  Evaluation length: {len(data['evaluation'])} characters")
    
    # Final GPU status
    print(f"\n{'='*60}")
    print("FINAL GPU STATUS")
    print(f"{'='*60}")
    final_gpus = get_gpu_info()
    if final_gpus:
        for gpu in final_gpus:
            print(f"GPU {gpu['index']} ({gpu['name']}): "
                  f"{gpu['memory_used']}/{gpu['memory_total']} MB, "
                  f"{gpu['utilization']}% util, {gpu['temperature']}°C")

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    main()