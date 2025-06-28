import axios from "axios";

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
axios.defaults.headers.common["Authorization"] = assembleAuthHeader();
axios.defaults.headers.common["Content-Type"] = "application/json";

export const getAuth = () => {
  return axios
    .get("/api/me")
    .then((response) => {
      return response.data;
    })
    .catch((error) => {
      return error.response.data;
    });
};

export const createGame = (max_players: number) => {
  return axios
    .post("/api/games", {
      max_players: max_players,
    })
    .then((response) => {
      return response.data;
    })
    .catch((error) => {
      return error.response.data;
    });
};

export const getGames = () => {
  return axios
    .get("/api/games")
    .then((response) => {
      return response.data.games;
    })
    .catch((error) => {
      return error.response.data;
    });
};
