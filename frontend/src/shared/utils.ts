import type { Game } from "@/entities/types";
import classNames, { type Argument } from "classnames";
import { twMerge } from "tailwind-merge";

export const navigateTo = (path: string) => {
  location.assign(path);
};

export const navigateToGame = (game: Game | string) => {
  let gameUUID: string;
  if (typeof game === "string") {
    gameUUID = game;
  } else {
    gameUUID = game.uuid;
  }
  // location.assign(`/game/${gameUUID}`);
  navigateTo(`/game/${gameUUID}`);
};

export const buildGameWebsocketUrl = (gameUUID: string) => {
  const path = "ws/game/" + gameUUID;
  const protocol = import.meta.env.VITE_USE_WSS == "True" ? "wss" : "ws";

  return `${protocol}://${window.location.host}/${path}/?${Telegram.WebApp.initData}`;
};

export const sleep = async (ms: number) => {
  return new Promise((r) => setTimeout(r, ms));
};

export const cn = (...inputs: Argument[]) => {
  return twMerge(classNames(...inputs));
};
