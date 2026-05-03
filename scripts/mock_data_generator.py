#!/usr/bin/env python3
"""
Mock Data Generator for IMS
Simulates failure scenarios across distributed systems
"""

import requests
import random
import time
from datetime import datetime
import json

API_URL = "http://localhost:8000/api/signals"

# Component types from requirements
COMPONENTS = [
    # RDBMS - P0 Priority
    "RDBMS_MASTER_01",
    "RDBMS_REPLICA_01",
    "RDBMS_REPLICA_02",
    
    # APIs - P0 Priority
    "API_GATEWAY_01",
    "API_USER_SERVICE",
    "API_AUTH_SERVICE",
    
    # MCP Hosts - P1 Priority
    "MCP_HOST_01",
    "MCP_HOST_02",
    
    # Distributed Caches - P2 Priority
    "CACHE_CLUSTER_01",
    "CACHE_CLUSTER_02",
    "CACHE_REDIS_MASTER",
    
    # Async Queues - P1 Priority
    "QUEUE_RABBITMQ_01",
    "QUEUE_KAFKA_BROKER_01",
    
    # NoSQL - P1 Priority
    "NOSQL_MONGODB_01",
    "NOSQL_CASSANDRA_01"
]

ERROR_TYPES = [
    "CONNECTION_TIMEOUT",
    "CONNECTION_REFUSED",
    "OUT_OF_MEMORY",
    "DISK_FULL",
    "HIGH_LATENCY",
    "SERVICE_UNAVAILABLE",
    "AUTHENTICATION_FAILED",
    "RATE_LIMIT_EXCEEDED"
]

def generate_signal(component_id: str):
    """Generate a realistic error signal"""
    error_type = random.choice(ERROR_TYPES)
    
    signal = {
        "component_id": component_id,
        "error_message": f"{error_type}: {component_id} is experiencing issues",
        "error_type": error_type,
        "severity": get_severity(component_id),
        "metadata": {
            "host": f"host-{random.randint(1, 10)}",
            "pod": f"pod-{random.randint(1, 100)}",
            "region": random.choice(["us-east-1", "us-west-2", "eu-west-1"]),
            "timestamp": datetime.utcnow().isoformat()
        }
    }
    
    return signal

def get_severity(component_id: str):
    """Determine severity based on component type"""
    if "RDBMS" in component_id or "API" in component_id:
        return "CRITICAL"
    elif "MCP" in component_id or "QUEUE" in component_id:
        return "HIGH"
    else:
        return "MEDIUM"

def simulate_burst(component_id: str, count: int = 100):
    """Simulate burst of signals for debouncing test"""
    print(f"\n🔥 Simulating burst: {count} signals for {component_id}")
    
    for i in range(count):
        signal = generate_signal(component_id)
        try:
            response = requests.post(API_URL, json=signal, timeout=1)
            if i % 20 == 0:
                print(f"  Sent {i+1}/{count} signals...")
        except Exception as e:
            print(f"  Error: {e}")
        
        time.sleep(0.01)  # 10ms between signals
    
    print(f"✅ Burst complete! Wait 10 seconds for debouncing...")

def simulate_continuous_load(duration_seconds: int = 60, rate: int = 100):
    """Simulate continuous load across all components"""
    print(f"\n🚀 Simulating continuous load: {rate} signals/sec for {duration_seconds}s")
    
    start_time = time.time()
    count = 0
    
    while time.time() - start_time < duration_seconds:
        component = random.choice(COMPONENTS)
        signal = generate_signal(component)
        
        try:
            requests.post(API_URL, json=signal, timeout=0.5)
            count += 1
            
            if count % 100 == 0:
                print(f"  Sent {count} signals...")
            
            time.sleep(1 / rate)  # Maintain desired rate
        except Exception as e:
            print(f"  Error: {e}")
    
    print(f"✅ Load test complete! Sent {count} signals")

def simulate_cascading_failure():
    """Simulate a realistic cascading failure scenario"""
    print("\n💥 Simulating cascading failure scenario...")
    
    scenarios = [
        {
            "description": "RDBMS Master Failure",
            "component": "RDBMS_MASTER_01",
            "count": 150,
            "delay": 2
        },
        {
            "description": "API Gateway starts failing (dependent on RDBMS)",
            "component": "API_GATEWAY_01",
            "count": 200,
            "delay": 3
        },
        {
            "description": "Cache cluster overwhelmed",
            "component": "CACHE_CLUSTER_01",
            "count": 100,
            "delay": 2
        },
        {
            "description": "Queue backing up",
            "component": "QUEUE_RABBITMQ_01",
            "count": 80,
            "delay": 1
        }
    ]
    
    for scenario in scenarios:
        print(f"\n  📍 {scenario['description']}")
        simulate_burst(scenario['component'], scenario['count'])
        time.sleep(scenario['delay'])
    
    print("\n✅ Cascading failure simulation complete!")

def menu():
    """Interactive menu"""
    print("\n" + "="*60)
    print("  IMS Mock Data Generator")
    print("="*60)
    print("\nChoose scenario:")
    print("  1. Single component burst (debouncing test)")
    print("  2. Continuous load test (high throughput)")
    print("  3. Cascading failure scenario (realistic)")
    print("  4. Custom load")
    print("  0. Exit")
    print("="*60)
    
    choice = input("\nEnter choice: ")
    
    if choice == "1":
        component = random.choice(COMPONENTS)
        simulate_burst(component, 100)
    
    elif choice == "2":
        duration = int(input("Duration (seconds, default=60): ") or 60)
        rate = int(input("Rate (signals/sec, default=100): ") or 100)
        simulate_continuous_load(duration, rate)
    
    elif choice == "3":
        simulate_cascading_failure()
    
    elif choice == "4":
        component = input(f"Component ID (e.g., {COMPONENTS[0]}): ")
        count = int(input("Number of signals: "))
        simulate_burst(component, count)
    
    elif choice == "0":
        print("\n👋 Goodbye!")
        exit()
    
    else:
        print("❌ Invalid choice")

if __name__ == "__main__":
    print("\n🎯 Waiting for backend to be ready...")
    time.sleep(2)
    
    # Check if backend is running
    try:
        response = requests.get("http://localhost:8000/health")
        print("✅ Backend is ready!\n")
    except:
        print("❌ Backend is not running! Start it first with: docker-compose up")
        exit(1)
    
    while True:
        menu()
        input("\nPress Enter to continue...")
