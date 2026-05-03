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
        
        # Import metrics
        try:
            from ..metrics import signals_total, buffer_size
            signals_total.inc()
        except Exception as e:
            print(f"⚠️ Metrics error: {e}")
        
        # Rate limiting
        if self.signal_counter["count"] > 10000:
            if time.time() - self.signal_counter["last_reset"] < 1:
                raise Exception("Rate limit exceeded")
        
        # Add to buffer
        signal["timestamp"] = datetime.utcnow().isoformat()
        self.signal_buffer.append(signal)
        self.signal_counter["count"] += 1
        
        # Update metrics
        try:
            from ..metrics import buffer_size
            buffer_size.set(len(self.signal_buffer))
        except:
            pass
        
        # Group by component
        component_id = signal["component_id"]
        self.component_signals[component_id].append(signal)
        
        print(f"📊 Component {component_id} now has {len(self.component_signals[component_id])} signals")
        
        # Trigger debouncing (REDUCED TO 2 SIGNALS)
        if len(self.component_signals[component_id]) >= 2:
            print(f"🔔 Threshold reached for {component_id}, creating work item...")
            asyncio.create_task(self.create_work_item_now(component_id))
        
        return {"status": "accepted", "buffer_size": len(self.signal_buffer)}
    
    async def create_work_item_now(self, component_id: str):
        """Create work item immediately when threshold reached"""
        signals = self.component_signals.get(component_id, [])
        
        if len(signals) == 0:
            print(f"⚠️ No signals for {component_id}")
            return
        
        print(f"💾 Creating work item for {component_id} with {len(signals)} signals...")
        
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
                
                total_active = db.query(WorkItem).filter(
                    WorkItem.state.in_(["OPEN", "INVESTIGATING", "RESOLVED"])
                ).count()
                active_incidents_count.set(total_active)
            except Exception as e:
                print(f"⚠️ Metrics update error: {e}")
            
            print(f"✅ Created Work Item #{work_item.id} for {component_id} (severity: {severity})")
            
            # Clear processed signals
            self.component_signals[component_id] = []
            
        except Exception as e:
            print(f"❌ Error creating work item: {e}")
            import traceback
            traceback.print_exc()
        finally:
            db.close()
    
    async def debounce_signals(self, component_id: str):
        """Legacy debouncing method (now using immediate creation)"""
        await asyncio.sleep(5)
        await self.create_work_item_now(component_id)
    
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
            rate = self.signal_counter["count"] / 5
            print(f"📊 [METRICS] Signals/5s: {self.signal_counter['count']} | "
                  f"Rate: {rate:.2f}/s | "
                  f"Buffer: {len(self.signal_buffer)} | "
                  f"Components: {len(self.component_signals)}")
            self.signal_counter["count"] = 0
            self.signal_counter["last_reset"] = time.time()
