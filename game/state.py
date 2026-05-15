# Import Enum class for creating enumeration types
from enum import Enum, auto

# Enumeration defining different AI states for robot behavior
class State(Enum):
    # PATROL state: robot wanders randomly around the map (passive behavior)
    PATROL = auto()
    # CHASE state: robot actively pursues player when detected (active behavior)
    CHASE = auto()
    # SEARCH state: robot searches last known player position (not yet implemented)
    SEARCH = auto()
    # TODO: Interception state to be added later for intercepting player movement