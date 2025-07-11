export const rollDiceSimpleEvent = {
  type: "game.event",
  game: {
    uuid: "0c23c860-aebc-44f7-99e1-f8b32e973a52",
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
          "https://a-ttgme.stel.com/i/userpic/320/km3Kt2Xui5sV_iITWLc7vA3Cq5svooSqa29PcQpToEfRtOLHVNLZhpmxXBImuJBH.svg",
        name: "ooooo",
      },
      {
        id: 2,
        position: 13,
        cash: 10,
        color: "red",
        rolled_double: false,
        double_count: 0,
        in_jail: false,
        jail_turns: 0,
        move_backwards: false,
        status: "playing",
        avatar:
          "https://a-ttgme.stel.com/i/userpic/320/nG-zbLjFwgajwIVtHiQjS5YLYmwfOj_MhhQCc2A9s6TulwyGlHs_Wm7tgMDa9f-T.svg",
        name: "аня",
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
        "https://a-ttgme.stel.com/i/userpic/320/km3Kt2Xui5sV_iITWLc7vA3Cq5svooSqa29PcQpToEfRtOLHVNLZhpmxXBImuJBH.svg",
      name: "ooooo",
    },
    {
      id: 2,
      position: 13,
      cash: 10,
      color: "red",
      rolled_double: false,
      double_count: 0,
      in_jail: false,
      jail_turns: 0,
      move_backwards: false,
      status: "playing",
      avatar:
        "https://a-ttgme.stel.com/i/userpic/320/nG-zbLjFwgajwIVtHiQjS5YLYmwfOj_MhhQCc2A9s6TulwyGlHs_Wm7tgMDa9f-T.svg",
      name: "аня",
    },
  ],
  events: [
    {
      event_type: "player.roll_dice",
      extra_data: {
        player: 2,
        dice_values: [3, 6],
      },
    },
    {
      event_type: "player.move",
      extra_data: {
        player: 2,
        position: 13,
      },
    },
  ],
};
