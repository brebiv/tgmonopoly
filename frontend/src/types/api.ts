export enum TileType {
  START = "START",
  PROPERTY = "PROPERTY",
  CHANCE = "CHANCE",
  TAX = "TAX",
  UTILITY = "UTILITY",
  JAIL = "JAIL",
  CASINO = "CASINO",
  POLICE = "POLICE",
}

export enum GameStatus {
  WAITING = "WAITING",
  PLAYING = "PLAYING",
  FINISHED = "FINISHED",
}

export enum GameEventScope {
  GAME = "game",
}

export enum GameEventType {
  GAME_CONNECTED = "game.connected",
}

export enum GameActionType {
  START_GAME = "start_game",
  ROLL_DICE = "roll_dice",
  MOVE_PLAYER = "move_player",
  BUY_PROPERRTY = "buy_property",
  PASSED_START = "passed_start",
  PAY_RENT = "pay_rent",
  PAY_FOR_PRISON = "pay_for_prison",
}

export enum GameEffectType {
  START_GAME = "start_game",
  ROLL_DICE = "roll_dice",
  ASK_BUY = "ask_buy",
  PAY_RENT = "pay_rent",
}

export enum PlayerStatus {
  WAITING = "waiting",
  PLAYING = "playing",
  WON = "won",
  LOST = "lost",
  TIMEOUT = "timeout",
}

// Enums end here

export type PropertyData = {
  id: number;
  price: number;
  mortgage_value: number;
  house_price: number;
  rent: number;
  rent_with_1_house: number;
  rent_with_2_houses: number;
  rent_with_3_houses: number;
  rent_with_4_houses: number;
  rent_with_5_houses: number;
  group_id: number;
  group_color: string;
  icon: string;
};

export type Tile = {
  id: number;
  position: number;
  name: string;
  type: TileType;
  propertyData: PropertyData | null;
};

export type EffectData = {
  price: number;
  rent: number;
  timeout: number;
  created: number;
};

export type GameEffect = {
  name: GameEffectType;
  effect_data: EffectData | null;
};

export type Player = {
  id: number;
  position: number;
  cash: number;
  color: string;
  in_jail: boolean;
  jail_turns: number;
  effects: GameEffect[];
  name: string;
  avatar: string;
  status: PlayerStatus;
};

export type PlayerChip = Player & {
  x: number | undefined;
  y: number | undefined;
};

export type Game = {
  uuid: string;
  max_players: number;
  current_player: number | null;
  turn: number;
  status: GameStatus;
  created: string;
};

export type GameEvent = {
  type: GameEventType | null;
  action: GameActionType | null;
  player: number | null;
  dices: number[] | null;
  position: number | null;
};

export type GameFrame = {
  type: GameEventType;
  action: GameActionType | null;
  game: Game | null;
  players: Player[] | null;
  events: GameEvent[] | null;
  me: Player | null;
  ownerships: Ownership[] | null;
};

export type GameAction = {
  action: GameActionType;
  game_uuid: string;
};

export type JoinGameResponse = {
  status: "ok" | "!ok";
  next_url: string;
};

export type CreateGameResponse = {
  status: "ok" | "!ok";
  next_url: string;
};

export type Ownership = {
  player: number;
  property: number;
  houses: number;
  mortgaged: boolean;
};
