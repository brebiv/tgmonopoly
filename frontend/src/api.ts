import { Tile } from "./types/api";

export const getTiles = () => {
  //@ts-ignore
  if (window && window.tiles) {
    // If tiles are available on the window object, return them as a resolved Promise
    // @ts-ignore
    return Promise.resolve(window.tiles as Tile[]);
  }

  // If not available, fetch the tiles from the API
  //   return fetch("/api/tiles/")
  //     .then((response) => response.json())
  //     .then((data) => data as Tile[]);
};
