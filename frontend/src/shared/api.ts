import axios from "axios";
import type { CreateGameResponse, JoinGameResponse } from "./api.types";
import type { BoardConfig } from "@/entities/types";

function assembleAuthHeader() {
  return `TWA ${Telegram.WebApp.initData}`;
}

// function getCsrfToken() {
//   return (
//     document
//       .querySelector('meta[name="csrf-token"]')
//       ?.getAttribute("content") || ""
//   );
// }

// axios.defaults.headers.common["X-CSRFToken"] = getCsrfToken();
// axios.defaults.headers.common["Authorization"] = assembleAuthHeader();
// axios.defaults.headers.common["Content-Type"] = "application/json";

// export const api = axios.create({
//   // baseURL: "feffw",
//   // timeout: 1000,
//   headers: {
//     Authorization: assembleAuthHeader(),
//     "Content-Type": "application/json",
//   },
// });

const initAPI = () => {
  return axios.create({
    // baseURL: "feffw",
    // timeout: 1000,
    headers: {
      Authorization: assembleAuthHeader(),
      "Content-Type": "application/json",
    },
  });
};

export const getAuth = () => {
  const api = initAPI();
  return api.get("/api/me/").then((response) => {
    return response.data;
  });
};

export const getGames = () => {
  const api = initAPI();
  return api.get("/api/games/").then((response) => {
    return response.data;
  });
};

export const createGame = async (max_players: number, config = "classic"): Promise<CreateGameResponse> => {
  try {
    const api = initAPI();
    const response = await api.post("/api/games/", {
      max_players: max_players,
      config: config,
    });
    return response.data;
  } catch (err: any) {
    if (err.response) {
      return Promise.reject(err.response.data);
    }
    return Promise.reject({ message: "Unknown error occurred" });
  }
};

export const joinGame = async (gameUUID: string): Promise<JoinGameResponse> => {
  try {
    const api = initAPI();
    const response = await api.post(`/api/games/${gameUUID}/join/`);
    return response.data;
  } catch (err: any) {
    if (err.response) {
      return Promise.reject(err.response.data);
    }
    return Promise.reject({ message: "Unknown error occurred" });
  }
};

export const leaveGame = async (gameUUID: string): Promise<JoinGameResponse> => {
  try {
    const api = initAPI();
    const response = await api.post(`/api/games/${gameUUID}/leave/`);
    return response.data;
  } catch (err: any) {
    if (err.response) {
      return Promise.reject(err.response.data);
    }
    return Promise.reject({ message: "Unknown error occurred" });
  }
};

export const getBoardConfig = async (name: string): Promise<BoardConfig> => {
  try {
    const api = initAPI();
    const response = await api.get(`/api/board_configs/${name}/`);
    return response.data;
  } catch (err: any) {
    if (err.response) {
      return Promise.reject(err.response.data);
    }
    return Promise.reject({ message: "Unknown error occurred" });
  }
};
