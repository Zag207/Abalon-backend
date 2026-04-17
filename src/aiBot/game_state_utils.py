from core.board.circle_team import CircleTeam


def get_team_code(circle_team: CircleTeam) -> int:
    match circle_team:
        case CircleTeam.White:
            return 1
        case CircleTeam.Black:
            return -1