import { http, HttpResponse, ws } from "msw";
import classic_board_config from "./classic_board_config";
import initial_game_frame from "./initial_game_frame";
import { rollDiceSimpleEvent } from "./rollDiceSimpleEvent";

const restHandlers = [
  http.get<never, never, string>("/api/board_configs/classic/", () => {
    // @ts-ignore
    // it's actually take object, not a string. i think there is bug in typing
    return HttpResponse.json(classic_board_config);
  }),
];

const game = ws.link("ws://localhost:6006/ws/game/:uuid/");

const wsHandlers = [
  game.addEventListener("connection", ({ client }) => {
    client.send(JSON.stringify(initial_game_frame));
    client.addEventListener("message", (event) => {
      event.preventDefault();
      if (event.data === "roll_dice") {
        client.send(JSON.stringify(rollDiceSimpleEvent));
      }
    });
  }),
];

export const handlers = [...restHandlers, ...wsHandlers];
