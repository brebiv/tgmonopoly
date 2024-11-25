import { useGameStore } from "@/stores/GameStore";
import { Ownership, Player, Tile } from "@/types/api";
import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";
import { queryClient } from "./queryClient";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function buildGameWebsocketUrl(gameUUID: string) {
  const path = "ws/game/" + gameUUID;
  const protocol = import.meta.env.VITE_USE_HTTPS === "true" ? "wss" : "ws";

  return (
    `${protocol}://${window.location.host}/${path}/` +
    // @ts-ignore
    `?${window.Telegram.WebApp.initData}`
  );
}

export async function sleep(ms: number) {
  return new Promise((r) => setTimeout(r, ms));
}

export function getTileFromPosition(tiles: Tile[], position: number) {
  return tiles.find((tile) => tile.position === position);
}

export function getTileFromId(tiles: Tile[], id: number) {
  return tiles.find((tile) => tile.id === id);
}

export function getMeFromPlayers(players: Player[]) {
  const me = useGameStore.getState().me;
  return players.find((player) => player.id === me?.id);
}

export function getPlayerByIdDepricated(players: Player[], id: number) {
  return players.find((player) => player.id === id);
}

export function getPlayerById(id: number) {
  const players = useGameStore.getState().players;
  if (!players) {
    return null;
  }
  return players.find((player) => player.id === id);
}

export function getPropertyById(id: number) {
  const tiles = queryClient.getQueriesData<Tile[]>(["tiles"])[0][1];
  if (!tiles) {
    return null;
  }
  return tiles.find((tile) => tile.propertyData?.id === id);
}

export function getOwnershipById(id: number) {
  let ownerships = queryClient.getQueriesData<Ownership[]>(["ownerships"])[0][1];
  if (!ownerships) {
    return null;
  }
  return ownerships.find((ownership) => ownership.id === id);
}

export function buildTradeMenuDataFromServerResponse(data: any) {
  let tradeMenuData = {
    from_player: data.from_player,
    to_player: data.to_player,
    cash_given: data.cash_given,
    cash_received: data.cash_received,
    ownerships: data.ownerships.map((ownership_id: number) => {
      // @ts-ignore
      return getOwnershipById(ownership_id);
    }),
  };

  return tradeMenuData;
}

export function hexToRGBA(hex: string, alpha: number) {
  // Remove the leading '#' if present
  hex = hex.replace(/^#/, "");

  // Parse the hex string into RGB values
  let r, g, b;
  if (hex.length === 3) {
    // If the hex is shorthand (e.g., #abc), expand it to full form
    r = parseInt(hex[0] + hex[0], 16);
    g = parseInt(hex[1] + hex[1], 16);
    b = parseInt(hex[2] + hex[2], 16);
  } else if (hex.length === 6) {
    r = parseInt(hex.substring(0, 2), 16);
    g = parseInt(hex.substring(2, 4), 16);
    b = parseInt(hex.substring(4, 6), 16);
  } else {
    throw new Error("Invalid hex color");
  }

  // Return the RGBA string with the alpha value
  return `rgba(${r}, ${g}, ${b}, ${alpha})`;
}
