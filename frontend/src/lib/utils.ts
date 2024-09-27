import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

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
