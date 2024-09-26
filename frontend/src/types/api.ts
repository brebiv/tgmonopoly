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

export type PropertyData = {
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

export type Player = {
  id: number;
  position: number;
  cash: number;
  color: string;
  in_jail: boolean;
  jail_turns: number;
};

export type PlayerChip = Player & {
  x: number | undefined;
  y: number | undefined;
};

export type Game = {
  uuid: string;
  max_players: number;
  turn: number;
  status: GameStatus;
  created: string;
};

export type GameEvent = {
  type: GameEventType;
  game: Game | null;
  players: Player[] | null;
};
