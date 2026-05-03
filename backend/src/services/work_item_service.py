from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Optional
from ..database import WorkItem, RCARecord, SessionLocal, redis_client
from ..patterns.state_pattern import StateManager
import json

class WorkItemService:
    def __init__(self):
        self.db = SessionLocal()
    
    async def create_work_item(self, component_id: str, severity: str, 
                               signal_ids: List[str], signal_count: int) -> dict:
        """Create a new work item in PostgreSQL"""
        try:
            work_item = WorkItem(
                component_id=component_id,
                severity=severity,
                state="OPEN",
                signal_count=signal_count
            )
            
            self.db.add(work_item)
            self.db.commit()
            self.db.refresh(work_item)
            
            work_item_dict = {
                "id": work_item.id,
                "component_id": work_item.component_id,
                "severity": work_item.severity,
                "state": work_item.state,
                "signal_count": work_item.signal_count,
                "created_at": work_item.created_at.isoformat(),
                "updated_at": work_item.updated_at.isoformat(),
                "signal_ids": signal_ids,
                "has_rca": False
            }
            
            # Cache in Redis
            try:
                redis_client.setex(
                    f"work_item:{work_item.id}",
                    3600,
                    json.dumps(work_item_dict)
                )
            except:
                pass  # Redis optional
            
            print(f"✅ Created Work Item {work_item.id}: {component_id}")
            return work_item_dict
            
        except Exception as e:
            self.db.rollback()
            print(f"❌ Create error: {e}")
            raise
    
    async def get_all_work_items(self, state: Optional[str] = None) -> List[dict]:
        """Get all work items from PostgreSQL"""
        try:
            print(f"📊 Fetching work items from database...")
            
            query = self.db.query(WorkItem)
            
            if state:
                query = query.filter(WorkItem.state == state)
            
            work_items = query.order_by(WorkItem.created_at.desc()).all()
            
            print(f"✅ Found {len(work_items)} work items in database")
            
            result = [{
                "id": wi.id,
                "component_id": wi.component_id,
                "severity": wi.severity,
                "state": wi.state,
                "signal_count": wi.signal_count,
                "created_at": wi.created_at.isoformat(),
                "updated_at": wi.updated_at.isoformat(),
                "has_rca": wi.rca is not None
            } for wi in work_items]
            
            print(f"✅ Returning {len(result)} incidents")
            return result
            
        except Exception as e:
            print(f"❌ Query error: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    async def get_work_item(self, work_item_id: int) -> Optional[dict]:
        """Get a specific work item"""
        try:
            # Try cache first
            try:
                cached = redis_client.get(f"work_item:{work_item_id}")
                if cached:
                    return json.loads(cached)
            except:
                pass
            
            # Fetch from DB
            work_item = self.db.query(WorkItem).filter(WorkItem.id == work_item_id).first()
            if not work_item:
                return None
            
            return {
                "id": work_item.id,
                "component_id": work_item.component_id,
                "severity": work_item.severity,
                "state": work_item.state,
                "signal_count": work_item.signal_count,
                "created_at": work_item.created_at.isoformat(),
                "updated_at": work_item.updated_at.isoformat(),
                "has_rca": work_item.rca is not None
            }
        except Exception as e:
            print(f"❌ Get work item error: {e}")
            return None
    
    async def transition_state(self, work_item_id: int, new_state: str) -> dict:
        """Transition work item to new state"""
        work_item = self.db.query(WorkItem).filter(WorkItem.id == work_item_id).first()
        
        if not work_item:
            raise Exception("Work item not found")
        
        work_item_dict = await self.get_work_item(work_item_id)
        is_valid, error = StateManager.validate_transition(
            work_item.state, 
            new_state, 
            work_item_dict
        )
        
        if not is_valid:
            raise Exception(error)
        
        work_item.state = new_state
        work_item.updated_at = datetime.utcnow()
        self.db.commit()
        
        try:
            redis_client.delete(f"work_item:{work_item_id}")
        except:
            pass
        
        return await self.get_work_item(work_item_id)
    
    async def create_rca(self, work_item_id: int, rca_data: dict) -> dict:
        """Create RCA for work item"""
        work_item = self.db.query(WorkItem).filter(WorkItem.id == work_item_id).first()
        
        if not work_item:
            raise Exception("Work item not found")
        
        start_time = rca_data["start_time"]
        end_time = rca_data["end_time"]
        mttr_seconds = int((end_time - start_time).total_seconds())
        
        rca = RCARecord(
            work_item_id=work_item_id,
            root_cause_category=rca_data["root_cause_category"],
            fix_applied=rca_data["fix_applied"],
            prevention_steps=rca_data["prevention_steps"],
            start_time=start_time,
            end_time=end_time,
            mttr_seconds=mttr_seconds
        )
        
        self.db.add(rca)
        self.db.commit()
        self.db.refresh(rca)
        
        try:
            redis_client.delete(f"work_item:{work_item_id}")
        except:
            pass
        
        return {
            "id": rca.id,
            "work_item_id": rca.work_item_id,
            "root_cause_category": rca.root_cause_category,
            "fix_applied": rca.fix_applied,
            "prevention_steps": rca.prevention_steps,
            "mttr_seconds": rca.mttr_seconds,
            "start_time": rca.start_time.isoformat(),
            "end_time": rca.end_time.isoformat()
        }
