from enum import Enum

class CircleTeam(Enum):
    Black = "black"
    White = "white"

def get_enemy_team(curr_team: CircleTeam) -> CircleTeam:
    match curr_team:
        case CircleTeam.Black:
            return CircleTeam.White
        case CircleTeam.White:
            return CircleTeam.Black
