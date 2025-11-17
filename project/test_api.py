"""
API Testing Script
Run with: python test_api.py
"""
import requests
import json
import time
import sys

BASE_URL = "http://localhost:8000"

def print_section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")

def test_health():
    """Test health check endpoint"""
    print_section("TEST 1: Health Check")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status Code: {response.status_code}")
    print(f"Response:\n{json.dumps(response.json(), indent=2)}")
    return response.status_code == 200

def test_analyze_pr():
    """Test PR analysis endpoint"""
    print_section("TEST 2: Queue PR Analysis")
    
    payload = {
        "repo_url": "https://github.com/facebook/react",
        "pr_number": 27663,
        "github_token": None
    }
    
    print(f"Request Payload:\n{json.dumps(payload, indent=2)}")
    response = requests.post(f"{BASE_URL}/analyze-pr", json=payload)
    
    print(f"\nStatus Code: {response.status_code}")
    data = response.json()
    print(f"Response:\n{json.dumps(data, indent=2)}")
    
    if response.status_code != 200:
        return None
    
    return data.get("task_id")

def test_status(task_id):
    """Test status check endpoint"""
    print_section("TEST 3: Check Task Status")
    
    response = requests.get(f"{BASE_URL}/status/{task_id}")
    print(f"Status Code: {response.status_code}")
    data = response.json()
    print(f"Response:\n{json.dumps(data, indent=2, default=str)}")
    
    return data.get("status")

def test_results(task_id):
    """Test results endpoint"""
    print_section("TEST 4: Get Analysis Results")
    
    response = requests.get(f"{BASE_URL}/results/{task_id}")
    print(f"Status Code: {response.status_code}")
    data = response.json()
    
    # Pretty print
    print(f"Response:")
    print(json.dumps(data, indent=2, default=str))
    
    return response.status_code == 200

def test_list_tasks():
    """Test list tasks endpoint"""
    print_section("TEST 5: List Recent Tasks")
    
    response = requests.get(f"{BASE_URL}/tasks?limit=5")
    print(f"Status Code: {response.status_code}")
    data = response.json()
    
    print(f"Response:")
    print(json.dumps(data, indent=2, default=str))
    
    return response.status_code == 200

def main():
    print("=" * 60)
    print("  AI CODE REVIEW SYSTEM - API TESTS")
    print("=" * 60)
    
    # Test 1: Health check
    if not test_health():
        print("\n❌ Health check failed! Is the API running?")
        print("Start the API with: python -m uvicorn app.main:app --reload")
        sys.exit(1)
    
    print("\n✅ Health check passed!")
    
    # Test 2: Queue PR
    task_id = test_analyze_pr()
    if not task_id:
        print("\n❌ Failed to queue PR analysis")
        sys.exit(1)
    
    print(f"\n✅ PR queued successfully! Task ID: {task_id}")
    
    # Test 3: Check status
    status = test_status(task_id)
    print(f"\n✅ Task Status: {status}")
    
    # Wait for processing
    if status == "pending":
        print("\n⏳ Waiting for task to start processing (30 seconds)...")
        for i in range(6):
            time.sleep(5)
            status = test_status(task_id)
            print(f"   Status check #{i+1}: {status}")
            if status != "pending":
                break
    
    # Test 4: Get results
    time.sleep(10)
    test_results(task_id)
    
    # Test 5: List tasks
    test_list_tasks()
    
    print("\n" + "=" * 60)
    print("  TESTS COMPLETED")
    print("=" * 60)

if __name__ == "__main__":
    main()
