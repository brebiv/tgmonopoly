import { TradeMenuData } from "@/stores/TradeStore";

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

export enum GameScopeType {
  GAME_CONNECTED = "game.connected",
  GAME_ACTION = "game.action",
  GAME_SERVICE = "game.service",
}

export enum GameEventType {
  REJECT_CASINO = "reject_casino",
  WON_CASINO = "won_casino",
  LOST_CASINO = "lost_casino",
  BUY_PROPERTY = "buy_property",
  GO_TO_PRISON = "go_to_prison",
  PAY_FOR_PRISON = "pay_for_prison",
  PRISON_RELEASE_FAIL = "prison_release_fail",
  RELEASE_FROM_PRISON = "release_from_prison",
  PAY_RENT = "pay_rent",
  CHANCE_CARD = "chance_card",
  STEPPED_ON_OWN_PROPERTY = "stepped_on_own_property",
  PAY_TO_BANK = "pay_to_bank",
  TIMEOUT = "timeout",
  CREATE_TRADE = "create_trade",
  REJECT_TRADE = "reject_trade",
  ACCEPT_TRADE = "accept_trade",
  START_AUCTION = "start_auction",
  REJECT_AUCTION = "reject_auction",
  ACCEPT_AUCTION = "accept_auction",
  WON_AUCTION = "won_auction",
  PLAYER_JOINED = "player_joined",
  PLAYER_LEFT = "player_left",
}

export enum GameActionType {
  START_GAME = "start_game",
  ROLL_DICE = "roll_dice",
  MOVE_PLAYER = "move_player",
  BUY_PROPERRTY = "buy_property",
  PASSED_START = "passed_start",
  PAY_RENT = "pay_rent",
  PAY_FOR_PRISON = "pay_for_prison",
  MORTAGE_PROPERTY = "mortage_property",
  BUYOUT_PROPERTY = "buyout_property",
  BUY_HOUSE = "buy_house",
  SELL_HOUSE = "sell_house",
  PAY = "pay",
  REJECT = "reject",
  ACCEPT = "accept",
  GO_TO_CASINO = "go_to_casino",
  WON_CASINO = "won_casino",
  LOST_CASINO = "lost_casino",
  CREATE_TRADE = "create_trade",
  START_AUCTION = "start_auction",
  NEXT_TURN = "next_turn",
}

export enum GameEffectType {
  START_GAME = "start_game",
  ROLL_DICE = "roll_dice",
  ASK_BUY = "ask_buy",
  PAY_RENT = "pay_rent",
  PAY_REPAIRS = "pay_repairs",
  IN_CASINO = "in_casino",
  IN_TRADE = "in_trade",
  IN_AUCTION = "in_auction",
}

export enum PlayerStatus {
  WAITING = "waiting",
  PLAYING = "playing",
  WON = "won",
  LOST = "lost",
  TIMEOUT = "timeout",
}

export enum SVGIcons {
  WIND_POWER = "WIND_POWER",
  DAM = "DAM",
  SOLAR_POWER = "SOLAR_POWER",
  NUKE = "NUKE",
}

export enum PropertyGroup {
  UTILITIES_1 = "UTILITIES_1",
  UTILITIES_2 = "UTILITIES_2",
  TECH = "TECH",
  FINANCE = "FINANCE",
  MEDECINE = "MEDECINE",
  OIL = "OIL",
  AUTOMOBILE = "AUTOMOBILE",
  COMMUNICATION = "COMMUNICATION",
  FOOD = "FOOD",
  CLOTH = "CLOTH",
}

export enum ChanceCardType {
  MOVE = "MOVE",
  MOVE_BACKWARDS = "MOVE_BACKWARDS",
  MONEY = "MONEY",
  MONEY_TO_PLAYER = "MONEY_TO_PLAYER",
  GO_TO_JAIL = "GO_TO_JAIL",
  FREE_JAIL = "FREE_JAIL",
  REPAIRS = "REPAIRS",
  MISC = "MISC",
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
  group_name: PropertyGroup;
  icon: string;
  buyout_price: number;
  svg_icon: SVGIcons | string;
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
  repair_cost: number;
  number_of_houses: number;
  house_repair_cost: number;
  timeout: number;
  created: number;
  available_bets: string[];
  current_player_in_auction: number | null;
  players_participating_in_auction: number[];
  current_auction_price: number;
  started_by: number;
  property: number;
} & TradeMenuData;

export type GameEffect = {
  name: GameEffectType;
  effect_data: EffectData | null;
};

export type PlayerPermissions = {
  abort_game: boolean | null;
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
  move_backwards: boolean;
  permissions: PlayerPermissions | null;
};

export type CompactPlayer = {
  id: number;
  name: string;
  color: string;
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
  players: CompactPlayer[];

  // GameList stuff
  in_game: boolean | null | undefined;
};

export type ChangeCardData = {
  title: string;
  description: string;
  card_type: ChanceCardType;
  details: string;
};

export type AuctionData = {
  started_by: number;
  current_player_in_auction: number;
  players_participating_in_auction: number[];
  current_auction_price: number;
  property: number;
  is_bet: boolean;
};

export type GameEvent = {
  type: GameScopeType | null;
  action: GameActionType | GameEventType | null;
  player: number | null;
  dices: number[] | null;
  position: number | null;
  amount: number | null;
  tile: number | null;
  tries_left: number | null;
  chance_card_data: ChangeCardData | null;
  to_player: number | null;
  auction_data: AuctionData | null;
};

export type GameFrame = {
  type: GameScopeType;
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
  extra_data?: any;
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
  id: number;
  player: number;
  property: number;
  houses: number;
  mortgaged: boolean;
  mortage_last_turn: number | null;
  can_build_house: boolean;
  can_sell_house: boolean;
  calculate_rent: number;
  owns_entire_group: boolean;
};

export type GamesResponse = {
  status: "ok" | "!ok";
  games: Game[];
  next_url: string | null;
};

export type UserPermissions = {
  create_game: boolean;
};

export type AuthMe = {
  first_name: string;
  id: number;
  language: string;
  last_name: string;
  permissions: UserPermissions;
  create_game: boolean;
  username: string;
};
