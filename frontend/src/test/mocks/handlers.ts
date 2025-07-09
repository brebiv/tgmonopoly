import { http, HttpResponse } from "msw";
import classic_board_config from "./classic_board_config";

export const handlers = [
  http.get<never, never, string>("/api/board_configs/classic/", () => {
    console.log("here");

    return HttpResponse.json(JSON.stringify(classic_board_config));
  }),
];
