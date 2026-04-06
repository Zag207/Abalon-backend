from enum import Enum


class MovingDirections(Enum):
    NoMove = 0
    UpRight = 1
    Right = 2
    DownRight = 3
    DownLeft = 4
    Left = 5
    UpLeft = 6

    @staticmethod
    def get_moving_vector(moving: MovingDirections) -> tuple[int, int]:
        """
        Возвращает вектор движения по направлению: (линия, диагональ)
        """
        moving_map = {
                MovingDirections.NoMove: (0, 0),
                MovingDirections.UpRight: (-1, 1),
                MovingDirections.Right: (0, 1),
                MovingDirections.DownRight: (1, 0),
                MovingDirections.DownLeft: (1, -1),
                MovingDirections.Left: (0, -1),
                MovingDirections.UpLeft: (-1, 0)
            }
        
        res = moving_map.get(moving)

        if res == None:
            raise ValueError(f"Moving direction value {moving} is not in moving_map")
        
        return res
