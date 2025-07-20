import type { GameActionCommand, GameActionType } from "@/entities/types";

export const generateActionCommand = (
  action: GameActionType,
  game_uuid: string,
  extra_data?: object,
): GameActionCommand => {
  const command = {
    action: action,
    game_uuid: game_uuid,
    extra_data: extra_data,
  };
  return command;
};
