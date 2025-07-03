export const ResponseStatuses = {
  OK: "ok",
  NOT_OK: "!ok",
} as const;

export type ResponseStatuses =
  (typeof ResponseStatuses)[keyof typeof ResponseStatuses];

type BaseApiResponse = {
  status: ResponseStatuses;
};

export type CreateGameResponse = {
  game_uuid: string;
} & BaseApiResponse;

export type JoinGameResponse = {
  game_uuid: string;
} & BaseApiResponse;

export type ErrorResponse = {};
