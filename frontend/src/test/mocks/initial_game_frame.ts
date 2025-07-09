import type { GameFrame } from "@/entities/types";

export default {
  type: "game.event",
  game: {
    uuid: "8c275279-cd26-4238-ad00-071267d45d8c",
    board_config: "classic",
    max_players: 2,
    turn: 1,
    current_player: 2,
    status: "PLAYING",
    players: [
      {
        id: 1,
        position: 0,
        cash: 10,
        color: "blue",
        rolled_double: false,
        double_count: 0,
        in_jail: false,
        jail_turns: 0,
        move_backwards: false,
        status: "playing",
        avatar:
          "https://a-ttgme.stel.com/i/userpic/320/nG-zbLjFwgajwIVtHiQjS5YLYmwfOj_MhhQCc2A9s6TulwyGlHs_Wm7tgMDa9f-T.svg",
        name: "\u0430\u043d\u044f",
      },
      {
        id: 2,
        position: 0,
        cash: 10,
        color: "red",
        rolled_double: false,
        double_count: 0,
        in_jail: false,
        jail_turns: 0,
        move_backwards: false,
        status: "playing",
        avatar:
          "https://a-ttgme.stel.com/i/userpic/320/km3Kt2Xui5sV_iITWLc7vA3Cq5svooSqa29PcQpToEfRtOLHVNLZhpmxXBImuJBH.svg",
        name: "ooooo",
      },
    ],
  },
  players: [
    {
      id: 1,
      position: 0,
      cash: 10,
      color: "blue",
      rolled_double: false,
      double_count: 0,
      in_jail: false,
      jail_turns: 0,
      move_backwards: false,
      status: "playing",
      avatar:
        "https://a-ttgme.stel.com/i/userpic/320/nG-zbLjFwgajwIVtHiQjS5YLYmwfOj_MhhQCc2A9s6TulwyGlHs_Wm7tgMDa9f-T.svg",
      name: "\u0430\u043d\u044f",
    },
    {
      id: 2,
      position: 0,
      cash: 10,
      color: "red",
      rolled_double: false,
      double_count: 0,
      in_jail: false,
      jail_turns: 0,
      move_backwards: false,
      status: "playing",
      avatar:
        "https://a-ttgme.stel.com/i/userpic/320/km3Kt2Xui5sV_iITWLc7vA3Cq5svooSqa29PcQpToEfRtOLHVNLZhpmxXBImuJBH.svg",
      name: "ooooo",
    },
  ],
  events: [],
} as GameFrame;
