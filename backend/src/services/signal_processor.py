from collections import defaultdict, deque
import asyncio
import time
from datetime import datetime
from ..database import SessionLocal, WorkItem

class SignalProcessor:
    def __init__(self):
        self.signal_buffer = deque(maxlen=100000)
        self.component_signals = defaultdict(list)
        self.signal_counter = {"count": 0, "last_reset": time.time()}
        print("✅ Signal Processor initialized")
    
    async def ingest_signal(self, signal: dict):
        print(f"📡 Received signal: {signal.get('component_id')}")
        
        # Import and update metrics
        try:
            from ..metrics import signals_total, buffer_size
            signals_total.inc()
            buffer_size.set(len(self.signal_buffer))
        except Exception as e:
            print(f"⚠️ Metrics error: {e}")
        
        # Add to buffer
        signal["timestamp"] = datetime.utcnow().isoformat()
        self.signal_buffer.append(signal)
        self.signal_counter["count"] += 1
        
        # Group by component
        component_id = signal["component_id"]
        self.component_signals[component_id].append(signal)
        
        print(f"📊 Component {component_id} now has {len(self.component_signals[component_id])} signals")
        
        # Create work item when threshold reached
        if len(self.component_signals[component_id]) >= 2:
            print(f"🔔 Threshold reached for {component_id}")
            asyncio.create_task(self.create_work_item_now(component_id))
        
        return {"status": "accepted", "buffer_size": len(self.signal_buffer)}
    
    async def create_work_item_now(self, component_id: str):
        """Create work item immediately"""
        signals = self.component_signals.get(component_id, [])
        
        if len(signals) == 0:
            return
        
        print(f"💾 Creating work item for {component_id}...")
        
        db = SessionLocal()
        try:
            severity = self.get_severity(component_id)
            
            work_item = WorkItem(
                component_id=component_id,
                severity=severity,
                state="OPEN",
                signal_count=len(signals)
            )
            
            db.add(work_item)
            db.commit()
            db.refresh(work_item)
            
            # Update metrics
            try:
                from ..metrics import incidents_total, active_incidents_count
                incidents_total.inc()
                
                # Count active incidents
                total_active = db.query(WorkItem).filter(
                    WorkItem.state.in_(["OPEN", "INVESTIGATING", "RESOLVED"])
                ).count()
                active_incidents_count.set(total_active)
                
                print(f"📊 Updated metrics - Total incidents: {incidents_total._value._value}")
            except Exception as e:
                print(f"⚠️ Metrics update error: {e}")
            
            print(f"✅ Created Work Item #{work_item.id} for {component_id}")
            
            # Clear buffer
            self.component_signals[component_id] = []
            
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            db.close()
    
    def get_severity(self, component_id: str) -> str:
        if "RDBMS" in component_id or "API" in component_id:
            return "CRITICAL"
        elif "CACHE" in component_id or "QUEUE" in component_id:
            return "HIGH"
        else:
            return "MEDIUM"
    
    async def print_metrics(self):
        while True:
            await asyncio.sleep(5)
            print(f"📊 [METRICS] Signals/5s: {self.signal_counter['count']} | "
                  f"Buffer: {len(self.signal_buffer)}")
            self.signal_counter["count"] = 0
            self.signal_counter["last_reset"] = time.time()
