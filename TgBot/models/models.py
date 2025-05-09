from typing import TypedDict, List, Optional

class Checkpoint(TypedDict):
    id: int
    name: str
    address: str
    type: str
    completed: bool

class RouteData(TypedDict):
    vehicle_info: str
    checkpoints: List[Checkpoint]
    current_checkpoint: Optional[int]