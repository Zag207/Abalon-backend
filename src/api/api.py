from typing import List
from uuid import UUID

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from aiBot.Bot import Bot
from aiBot.base_alpha_zero.utils import dotdict
from core.board.circle_team import CircleTeam, get_enemy_team
from core.game_state import GameState
from core.movement.moving_directions import MovingDirections
from core.setup.prepare_circles import fill_circle_board

app = FastAPI()


class CircleResponse(BaseModel):
	id: UUID
	line: int
	diagonal: int
	team: str


class MoveRequest(BaseModel):
	moving_team: str = Field(description="Название команды: black или white")
	circle_ids: List[UUID] = Field(description="Массив id фишек для передвижения")
	moving_direction: str = Field(description="Направление хода: UpRight, Right, DownRight, DownLeft, Left, UpLeft")


class MoveResponse(BaseModel):
	is_error: bool
	is_win: bool
	moved_circles: List[CircleResponse]
	moving_direction: str


class WinnerResponse(BaseModel):
	winner_team: str | None = Field(description="Значения: Чёрные, Белые, Ничья, None - игра продолжается")


class CurrentTeamResponse(BaseModel):
	curr_team: str

game_state = GameState(fill_circle_board())

bot_args = dotdict({
    "numMCTSSims": 50,
    "cpuct": 0.5
})
bot = Bot(game=game_state, player=CircleTeam.Black, args=bot_args)


def _parse_team(team_name: str) -> CircleTeam:
	normalized = team_name.strip().lower()
	for team in CircleTeam:
		if team.value == normalized:
			return team

	raise HTTPException(
		status_code=400,
		detail=f"Некорректная команда '{team_name}'. Используйте 'black' или 'white'.",
	)


def _parse_direction(direction_name: str) -> MovingDirections:
	normalized = direction_name.strip().lower().replace("_", "").replace("-", "").replace(" ", "")
	for direction in MovingDirections:
		if direction == MovingDirections.NoMove:
			continue

		if direction.name.lower() == normalized:
			return direction

	raise HTTPException(
		status_code=400,
		detail=(
			f"Некорректное направление '{direction_name}'. "
			"Используйте одно из: UpRight, Right, DownRight, DownLeft, Left, UpLeft."
		),
	)


def _serialize_board() -> List[CircleResponse]:
	return [
		CircleResponse(
			id=circle.circle_id,
			line=circle.coords.line,
			diagonal=circle.coords.diagonal,
			team=circle.circle_type.value,
		)
		for circle in game_state.get_circles()
	]


@app.get("/move_bot", response_model=MoveResponse)
def move_bot() -> MoveResponse:
	moving = bot.calc_move()
	moving_res = game_state._make_move(moving.circles_checked, moving.moving_direction, CircleTeam.Black)

	return MoveResponse(
		is_error=moving_res.is_error,
		is_win=moving_res.is_win,
		moved_circles=[
			CircleResponse(
				id=circle.circle_id,
				line=circle.coords.line,
				diagonal=circle.coords.diagonal,
				team=circle.circle_type.value,
			)
			for circle in moving_res.circles_moving
		],
		moving_direction=str(moving.moving_direction)
	)


@app.get("/board", response_model=List[CircleResponse])
def get_board() -> List[CircleResponse]:
	return _serialize_board()


@app.post("/move", response_model=MoveResponse)
def post_move(move_request: MoveRequest) -> MoveResponse:
	moving_team = _parse_team(move_request.moving_team)
	moving_direction = _parse_direction(move_request.moving_direction)

	if len(move_request.circle_ids) == 0:
		raise HTTPException(status_code=400, detail="Нужно передать хотя бы один id фишки")
	move_result = game_state.move(move_request.circle_ids, moving_direction, moving_team)

	if move_result.is_error:
		raise HTTPException(status_code=400, detail="Ход невалиден")

	return MoveResponse(
		is_error=move_result.is_error,
		is_win=move_result.is_win,
		moved_circles=[
			CircleResponse(
				id=circle.circle_id,
				line=circle.coords.line,
				diagonal=circle.coords.diagonal,
				team=circle.circle_type.value,
			)
			for circle in move_result.circles_moving
		],
		moving_direction=moving_direction.name,
	)

@app.get("/winner", response_model=WinnerResponse)
def get_winner() -> WinnerResponse:
	curr_team = game_state.curr_team
	curr_player_value = game_state.get_value_for_player(curr_team)

	if curr_player_value is None:
		return WinnerResponse(winner_team=None)
	elif curr_player_value == 0:
		return WinnerResponse(winner_team="Ничья")
	elif curr_player_value > 0:
		return WinnerResponse(winner_team=curr_team.value)
	else:
		return WinnerResponse(winner_team=get_enemy_team(curr_team).value)


@app.get("/moving-team", response_model=CurrentTeamResponse)
def get_moving_team() -> CurrentTeamResponse:
	return CurrentTeamResponse(curr_team=game_state.get_moving_team().value)

@app.put("/reload-game", response_model=List[CircleResponse])
def reload_game() -> List[CircleResponse]:
    global game_state
    game_state = GameState(fill_circle_board())
    return _serialize_board()

