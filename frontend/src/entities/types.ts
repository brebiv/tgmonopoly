export type User = {
  id: number;
  first_name: string;
  last_name: string;
  username: string;
  photo_url: string;
  language: string;
};

export type Me = {
  user: User;
  current_game: Object | null;
};

export const PlayerStatus = {
  WAITING: "waiting",
  PLAYING: "playing",
  WON: "won",
  LOST: "lost",
  TIMEOUT: "timeout",
} as const;

export const GameStatus = {
  WAITING: "WAITING",
  PLAYING: "PLAYING",
  FINISHED: "FINISHED",
  ABANDONED: "ABANDONED",
} as const;

export type PlayerStatus = (typeof PlayerStatus)[keyof typeof PlayerStatus];
export type GameStatus = (typeof GameStatus)[keyof typeof GameStatus];

export type Player = {
  avatar: string;
  cash: number;
  color: string;
  double_count: number;
  in_jail: boolean;
  jail_turns: number;
  move_backwards: boolean;
  position: number;
  rolled_double: boolean;
  status: PlayerStatus;
  name: string;
};

export type Game = {
  board_config: string;
  current_player: number;
  max_players: number;
  players: Player[];
  status: GameStatus;
  turn: number;
  uuid: string;
};
