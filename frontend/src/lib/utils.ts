import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function buildGameWebsocketUrl(gameUUID: string) {
  const path = "ws/game/" + gameUUID;

  return (
    `ws://${window.location.host}/${path}/` +
    // @ts-ignore
    `?${window.Telegram.WebApp.initData}`
  );
}
