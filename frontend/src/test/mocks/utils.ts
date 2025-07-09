import type { Player } from "@/entities/types";

export const createMockPlayer = (id: number, name: string, color: string): Player => {
  return {
    id: id,
    position: 0,
    cash: 10,
    color: color,
    rolled_double: false,
    double_count: 0,
    in_jail: false,
    jail_turns: 0,
    move_backwards: false,
    status: "playing",
    avatar: `https://api.dicebear.com/9.x/pixel-art/svg?seed=${id}.png`,
    name: name,
  };
};

// const generateRandomPlayers = (count: number): Player[] => Array.from({ length: count }, createMockPlayer);
