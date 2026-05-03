from abc import ABC, abstractmethod

class AlertStrategy(ABC):
    """Strategy Pattern for Alert Types"""
    
    @abstractmethod
    async def send_alert(self, work_item: dict) -> None:
        pass

class P0AlertStrategy(AlertStrategy):
    """Critical Priority Alert - RDBMS, API Gateway failures"""
    
    async def send_alert(self, work_item: dict) -> None:
        print(f"🚨 [P0 CRITICAL] Component: {work_item['component_id']} | "
              f"State: {work_item['state']} | Time: {work_item['created_at']}")
        # In production: Send to PagerDuty, Slack critical channel, SMS

class P1AlertStrategy(AlertStrategy):
    """High Priority Alert - MCP failures"""
    
    async def send_alert(self, work_item: dict) -> None:
        print(f"⚠️  [P1 HIGH] Component: {work_item['component_id']} | "
              f"State: {work_item['state']} | Time: {work_item['created_at']}")
        # In production: Send to Slack, Email to on-call

class P2AlertStrategy(AlertStrategy):
    """Medium Priority Alert - Cache failures"""
    
    async def send_alert(self, work_item: dict) -> None:
        print(f"ℹ️  [P2 MEDIUM] Component: {work_item['component_id']} | "
              f"State: {work_item['state']} | Time: {work_item['created_at']}")
        # In production: Log to monitoring system, Email

class AlertContext:
    """Context for executing alert strategies"""
    
    def __init__(self, strategy: AlertStrategy):
        self._strategy = strategy
    
    def set_strategy(self, strategy: AlertStrategy):
        self._strategy = strategy
    
    async def execute_alert(self, work_item: dict):
        await self._strategy.send_alert(work_item)

def get_alert_strategy(component_id: str) -> AlertStrategy:
    """Factory method to get appropriate alert strategy"""
    if "RDBMS" in component_id or "API" in component_id:
        return P0AlertStrategy()
    elif "MCP" in component_id or "QUEUE" in component_id:
        return P1AlertStrategy()
    else:  # CACHE, etc.
        return P2AlertStrategy()
