export enum TileType {
  START = "START",
  PROPERTY = "PROPERTY",
  CHANCE = "CHANCE",
  TAX = "TAX",
  UTILITY = "UTILITY",
  UTILITY_2 = "UTILITY_2",
  JAIL = "JAIL",
  CASINO = "CASINO",
  POLICE = "POLICE",
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
