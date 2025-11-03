#!/usr/bin/env python3
"""
Compare different Ollama models for ASP trainee response evaluation
"""
import os
import requests
import json
import time
from datetime import datetime

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
    
    start_time = time.time()
    try:
        response = requests.post(url, json=payload, timeout=120)
        response.raise_for_status()
        elapsed = time.time() - start_time
        
        result = response.json()
        print(f"Response time: {elapsed:.2f} seconds")
        print("\nEvaluation:")
        print(result.get('response', 'No response'))
        
        return result.get('response', 'No response'), elapsed
    except Exception as e:
        print(f"Error: {e}")
        return None, 0

def main():
    # Sample scenario and trainee response
    scenario = """
    A 68-year-old patient presents with suspected community-acquired pneumonia. 
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

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    main()