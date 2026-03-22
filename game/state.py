from enum import Enum, auto

class State(Enum):
    PATROL = auto()
    CHASE = auto()
    SEARCH = auto()
    # Inteception state to be added