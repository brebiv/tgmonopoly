import { http, HttpResponse, ws } from "msw";
import classic_board_config from "./classic_board_config";
import initial_game_frame from "./initial_game_frame";

const restHandlers = [
  http.get<never, never, string>("/api/board_configs/classic/", () => {
    return HttpResponse.json(JSON.stringify(classic_board_config));
  }),
];

const game = ws.link("ws://localhost:6006/ws/game/:uuid/");

const wsHandlers = [
  game.addEventListener("connection", ({ client }) => {
    client.send(JSON.stringify(initial_game_frame));
  }),
];

export const handlers = [...restHandlers, ...wsHandlers];
