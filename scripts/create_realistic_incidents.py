#!/usr/bin/env python3
"""
Generate realistic production incidents for Zeotap IMS
Simulates real-world distributed system failures
"""

import requests
import time
from datetime import datetime
import random

BASE_URL = "http://localhost:8000"

# Realistic incident scenarios
INCIDENTS = [
    # 1. Database Connection Pool Exhaustion
    {
        "component_id": "RDBMS_MASTER_01",
        "signals": [
            {
                "error_message": "Connection pool exhausted: all 200 connections in use",
                "error_type": "CONNECTION_POOL_ERROR",
                "severity": "CRITICAL",
                "metadata": {
                    "host": "db-master-01.prod.zeotap.com",
                    "port": 5432,
                    "pool_size": 200,
                    "active_connections": 200,
                    "waiting_requests": 1547
                }
            },
            {
                "error_message": "Connection wait timeout after 30000ms",
                "error_type": "CONNECTION_TIMEOUT",
                "severity": "CRITICAL",
                "metadata": {
                    "timeout_ms": 30000,
                    "queue_depth": 1547
                }
            }
        ]
    },
    
    # 2. API Gateway High Latency
    {
        "component_id": "API_GATEWAY_01",
        "signals": [
            {
                "error_message": "Response time exceeded SLA: 8547ms > 1000ms threshold",
                "error_type": "HIGH_LATENCY",
                "severity": "CRITICAL",
                "metadata": {
                    "response_time_ms": 8547,
                    "threshold_ms": 1000,
                    "endpoint": "/api/v2/analytics/reports",
                    "method": "POST"
                }
            },
            {
                "error_message": "Upstream service timeout: analytics-service unreachable",
                "error_type": "UPSTREAM_TIMEOUT",
                "severity": "CRITICAL",
                "metadata": {
                    "upstream": "analytics-service.internal",
                    "timeout_after": "5s"
                }
            }
        ]
    },
    
    # 3. Redis Cache Cluster Failure
    {
        "component_id": "CACHE_CLUSTER_01",
        "signals": [
            {
                "error_message": "Redis master node unreachable - ECONNREFUSED",
                "error_type": "CONNECTION_REFUSED",
                "severity": "HIGH",
                "metadata": {
                    "host": "redis-master-01.cache.internal",
                    "port": 6379,
                    "cluster_mode": "sentinel",
                    "failover_status": "in_progress"
                }
            },
            {
                "error_message": "Cache miss ratio: 94.7% (threshold: 20%)",
                "error_type": "HIGH_MISS_RATIO",
                "severity": "HIGH",
                "metadata": {
                    "miss_ratio": 94.7,
                    "threshold": 20.0,
                    "total_requests": 487532,
                    "cache_hits": 25839
                }
            }
        ]
    },
    
    # 4. Kafka Message Queue Lag
    {
        "component_id": "QUEUE_SERVICE_01",
        "signals": [
            {
                "error_message": "Consumer lag exceeds threshold: 2.4M messages behind",
                "error_type": "CONSUMER_LAG",
                "severity": "HIGH",
                "metadata": {
                    "topic": "user-events-prod",
                    "partition": 7,
                    "current_offset": 15847293,
                    "latest_offset": 18247158,
                    "lag": 2399865,
                    "consumer_group": "analytics-processors"
                }
            },
            {
                "error_message": "Kafka broker disk utilization: 91.2% (critical: 90%)",
                "error_type": "DISK_SPACE_CRITICAL",
                "severity": "HIGH",
                "metadata": {
                    "broker_id": 3,
                    "disk_used_gb": 912,
                    "disk_total_gb": 1000,
                    "utilization_percent": 91.2
                }
            }
        ]
    },
    
    # 5. MongoDB Replica Set Split Brain
    {
        "component_id": "NOSQL_DB_01",
        "signals": [
            {
                "error_message": "Replica set election failed - no primary elected",
                "error_type": "REPLICATION_ERROR",
                "severity": "MEDIUM",
                "metadata": {
                    "replica_set": "rs-analytics",
                    "members": 5,
                    "healthy_members": 2,
                    "election_attempts": 12,
                    "error": "insufficient voting members"
                }
            },
            {
                "error_message": "Write concern timeout: majority not acknowledged",
                "error_type": "WRITE_CONCERN_ERROR",
                "severity": "MEDIUM",
                "metadata": {
                    "write_concern": "majority",
                    "timeout_ms": 5000,
                    "acknowledged_by": 1,
                    "required": 3
                }
            }
        ]
    },
    
    # 6. Application Memory Leak
    {
        "component_id": "API_GATEWAY_02",
        "signals": [
            {
                "error_message": "Heap memory usage critical: 95.3% of 8GB",
                "error_type": "HIGH_MEMORY",
                "severity": "CRITICAL",
                "metadata": {
                    "heap_used_mb": 7624,
                    "heap_max_mb": 8000,
                    "utilization_percent": 95.3,
                    "gc_time_percent": 67.8,
                    "process_uptime_hours": 142
                }
            },
            {
                "error_message": "GC overhead limit exceeded - application degraded",
                "error_type": "GC_OVERHEAD",
                "severity": "CRITICAL",
                "metadata": {
                    "gc_time_ms": 45672,
                    "gc_overhead_percent": 67.8,
                    "threshold": 50.0
                }
            }
        ]
    },
    
    # 7. CDN Origin Server 5xx Errors
    {
        "component_id": "API_GATEWAY_03",
        "signals": [
            {
                "error_message": "High 5xx error rate: 23.4% (threshold: 1%)",
                "error_type": "HIGH_ERROR_RATE",
                "severity": "CRITICAL",
                "metadata": {
                    "error_rate_percent": 23.4,
                    "threshold_percent": 1.0,
                    "total_requests": 145872,
                    "error_count": 34134,
                    "time_window": "5m"
                }
            },
            {
                "error_message": "503 Service Unavailable - backend pool exhausted",
                "error_type": "SERVICE_UNAVAILABLE",
                "severity": "CRITICAL",
                "metadata": {
                    "status_code": 503,
                    "backend_pool": "api-workers",
                    "healthy_backends": 0,
                    "total_backends": 12
                }
            }
        ]
    },
    
    # 8. Elasticsearch Cluster Yellow Status
    {
        "component_id": "NOSQL_DB_02",
        "signals": [
            {
                "error_message": "Cluster status degraded to YELLOW - unassigned shards detected",
                "error_type": "CLUSTER_HEALTH",
                "severity": "MEDIUM",
                "metadata": {
                    "cluster_name": "logs-production",
                    "status": "yellow",
                    "active_shards": 487,
                    "unassigned_shards": 23,
                    "relocating_shards": 5,
                    "nodes": 9
                }
            },
            {
                "error_message": "Disk watermark threshold breached on node-07",
                "error_type": "DISK_WATERMARK",
                "severity": "MEDIUM",
                "metadata": {
                    "node": "es-node-07",
                    "disk_used_percent": 88.4,
                    "watermark_high": 85.0,
                    "disk_available_gb": 116
                }
            }
        ]
    },
    
    # 9. Network Latency Spike
    {
        "component_id": "CACHE_CLUSTER_02",
        "signals": [
            {
                "error_message": "Network latency spike detected: p99=847ms (baseline: 2ms)",
                "error_type": "NETWORK_LATENCY",
                "severity": "HIGH",
                "metadata": {
                    "latency_p50_ms": 234,
                    "latency_p99_ms": 847,
                    "latency_baseline_ms": 2,
                    "affected_route": "us-east-1 → us-west-2",
                    "packet_loss_percent": 4.7
                }
            },
            {
                "error_message": "Redis command timeout: GET operation exceeded 1000ms",
                "error_type": "COMMAND_TIMEOUT",
                "severity": "HIGH",
                "metadata": {
                    "command": "GET",
                    "key_pattern": "user:session:*",
                    "timeout_ms": 1000,
                    "actual_time_ms": 2847
                }
            }
        ]
    },
    
    # 10. SSL Certificate Expiry Warning
    {
        "component_id": "API_GATEWAY_04",
        "signals": [
            {
                "error_message": "SSL certificate expiring in 5 days",
                "error_type": "CERTIFICATE_EXPIRY",
                "severity": "MEDIUM",
                "metadata": {
                    "domain": "api.zeotap.com",
                    "expires_at": "2026-05-07T23:59:59Z",
                    "days_remaining": 5,
                    "issuer": "Let's Encrypt Authority X3",
                    "serial": "04:7A:F2:E9:B1:C4:5D:8F"
                }
            },
            {
                "error_message": "TLS handshake failures increasing: 147 failures/min",
                "error_type": "TLS_HANDSHAKE_ERROR",
                "severity": "MEDIUM",
                "metadata": {
                    "failures_per_minute": 147,
                    "baseline": 5,
                    "error_type": "certificate_unknown",
                    "client_ips_affected": 89
                }
            }
        ]
    }
]

def create_incident(incident_data):
    """Create an incident by sending multiple signals"""
    component_id = incident_data["component_id"]
    signals = incident_data["signals"]
    
    print(f"\n{'='*70}")
    print(f"🔧 Creating incident for: {component_id}")
    print(f"{'='*70}")
    
    for i, signal in enumerate(signals, 1):
        signal["component_id"] = component_id
        
        try:
            response = requests.post(
                f"{BASE_URL}/api/signals",
                json=signal,
                timeout=5
            )
            
            if response.status_code == 200:
                print(f"  ✅ [{i}/{len(signals)}] Signal sent: {signal['error_message'][:60]}...")
            else:
                print(f"  ❌ [{i}/{len(signals)}] Failed: {response.status_code}")
                
        except Exception as e:
            print(f"  ❌ [{i}/{len(signals)}] Error: {e}")
        
        time.sleep(0.5)  # Small delay between signals
    
    print(f"  ⏳ Waiting for debouncing (5 seconds)...")
    time.sleep(5)

def main():
    print("="*70)
    print("🚀 ZEOTAP IMS - Realistic Incident Generator")
    print("="*70)
    print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🎯 Target: {BASE_URL}")
    print(f"📊 Total incidents to create: {len(INCIDENTS)}")
    print("="*70)
    
    # Test backend connectivity
    try:
        health = requests.get(f"{BASE_URL}/health", timeout=5)
        print(f"✅ Backend health: {health.json().get('status', 'unknown')}")
    except Exception as e:
        print(f"❌ Backend unreachable: {e}")
        print("⚠️  Make sure backend is running: docker-compose up -d")
        return
    
    # Create all incidents
    for idx, incident in enumerate(INCIDENTS, 1):
        print(f"\n[{idx}/{len(INCIDENTS)}] Processing incident...")
        create_incident(incident)
        
        if idx < len(INCIDENTS):
            print(f"\n⏱️  Waiting 2 seconds before next incident...")
            time.sleep(2)
    
    # Final verification
    print("\n" + "="*70)
    print("🎉 All incidents created!")
    print("="*70)
    
    try:
        incidents_resp = requests.get(f"{BASE_URL}/api/incidents", timeout=5)
        incidents_data = incidents_resp.json()
        
        print(f"\n📊 Final Status:")
        print(f"  • Total incidents: {incidents_data.get('count', 0)}")
        print(f"  • Timestamp: {incidents_data.get('timestamp', 'N/A')}")
        
        # Count by severity
        incidents_list = incidents_data.get('incidents', [])
        critical = len([i for i in incidents_list if i['severity'] == 'CRITICAL'])
        high = len([i for i in incidents_list if i['severity'] == 'HIGH'])
        medium = len([i for i in incidents_list if i['severity'] == 'MEDIUM'])
        
        print(f"\n  Severity breakdown:")
        print(f"    🔴 CRITICAL: {critical}")
        print(f"    🟠 HIGH: {high}")
        print(f"    🟡 MEDIUM: {medium}")
        
        print(f"\n🌐 View in browser:")
        print(f"  • Frontend: http://localhost:3000")
        print(f"  • API Docs: http://localhost:8000/docs")
        print(f"  • Incidents: http://localhost:8000/api/incidents")
        
    except Exception as e:
        print(f"⚠️  Could not verify incidents: {e}")
    
    print("\n" + "="*70)
    print("✅ COMPLETE!")
    print("="*70 + "\n")

if __name__ == "__main__":
    main()
