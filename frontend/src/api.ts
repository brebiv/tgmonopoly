import { GameAction, Tile } from "./types/api";

import axios from "axios";

function assembleAuthHeader() {
  // @ts-ignore
  return `twa ${window.Telegram.WebApp.initData}`;
}

function getCsrfToken() {
  return document.querySelector('meta[name="csrf-token"]')?.getAttribute("content") || "";
}

axios.defaults.headers.common["X-CSRFToken"] = getCsrfToken();
axios.defaults.headers.common["Authorization"] = assembleAuthHeader();
axios.defaults.headers.common["Content-Type"] = "application/json";

export const getTiles = () => {
  //@ts-ignore
  if (window && window.tiles) {
    // If tiles are available on the window object, return them as a resolved Promise
    // @ts-ignore
    return Promise.resolve(window.tiles as Tile[]);
  }

  // If not available, fetch the tiles from the API
  //   return fetch("/api/tiles/")
  //     .then((response) => response.json())
  //     .then((data) => data as Tile[]);
};

export const getAuth = () => {
  return axios.get("/api/me/").then((response) => {
    return response.data;
  });
};

export const createGame = (maxPlayers: number) => {
  return axios.post("/api/create_game/", { max_players: maxPlayers }).then((response) => {
    return response.data;
  });
};

// @ts-ignore
export const getGame = (gameUuid: string) => {
  // @ts-ignore
  if (window && window.game) {
    // @ts-ignore
    return Promise.resolve(window.game as Game);
  }
};

// @ts-ignore
export const getPlayers = (gameUuid: string) => {
  // @ts-ignore
  if (window && window.players) {
    // @ts-ignore
    return Promise.resolve(window.players as Player[]);
  }
};

export const sendGameAction = (action: GameAction) => {
  return axios.post("/api/game_action/", action).then((response) => {
    return response.data;
  });
};
