import { PlayerStatus, type Player } from "@/entities/types";

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
    status: PlayerStatus.PLAYING,
    avatar: `https://api.dicebear.com/9.x/pixel-art/svg?seed=${id}.png`,
    name: name,
  };
};

export const generateRandomPlayers = (count: number): Player[] => {
  let colors = ["blue", "red", "green", "yellow"];
  let names = ["Leo", "Rick", "Morty", "Neo"];

  let players: Player[] = [];
  for (let i = 0; i < count; i++) {
    let color = colors[i % colors.length];
    let name = names[i % names.length];
    players.push(createMockPlayer(i + 1, name, color));
  }
  return players;
};
