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
  current_game: Game | null;
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
  id: number;
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

export const GameEventTypes = {
  PLAYER_JOINED: "player.joined",
  PLAYER_ACTION: "player.action",
} as const;
export type GameEventTypes = (typeof GameEventTypes)[keyof typeof GameEventTypes];

export type GameEvent = {
  event_type: GameEventTypes;
  action: string;
  player: number;
};

export type GameFrame = {
  events: GameEvent[];
  game: Game;
  players: Player[];
  my_player_id?: number;
  type: string;
};

export type PropertyGroup = {
  id: number;
  name: string;
  color: string;
};

export type UtilityGroup = {
  id: number;
  type: string;
  name: string;
  color: string;
};

const TileTypes = {
  START: "start",
  TAX: "tax",
  CHANCE: "chance",
  JAIL: "jail",
  POLICE: "police",
  CASINO: "casino",
  PROPERTY: "property",
  UTILITY: "utility",
} as const;
export type TileTypes = (typeof TileTypes)[keyof typeof TileTypes];

type Property = {
  price: number;
  mortgage_value: number;
  house_price: number;
  rent: number;
  rent_with_1_house: number;
  rent_with_2_houses: number;
  rent_with_3_houses: number;
  rent_with_4_houses: number;
  rent_with_5_houses: number;
  group: number;
  icon: string;
  mortgage_buyback_price: number;
};

type Utility = {
  price: number;
  mortgage_value: number;
  group: string;
  icon: string;
};

type BaseTile = {
  name: string;
  position: number;
  tile_type: TileTypes;
};

export type Tile = BaseTile & Property & Utility;

export type BoardConfig = {
  name: string;
  property_groups: PropertyGroup[];
  utility_groups: UtilityGroup[];
  tiles: Tile[];
};
