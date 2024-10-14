import { useEffect, useState, createContext } from "react";
import BoardTile from "./BoardTile";
import { useTiles } from "@/hooks";
import { useLayoutStore } from "@/stores/LayoutStore";

const boardContext = {
  gridCellWidth: 0,
  gridCellHeight: 0,
  cornerSizeInPercent: 12,
};

const BoardContext = createContext(boardContext);

function Board({ boardLoaded, setBoardLoaded }: { boardLoaded: boolean; setBoardLoaded: any }) {
  const [gridCellWidth, setGridCellWidth] = useState<number>(0);
  const [gridCellHeight, setGridCellHeight] = useState<number>(0);
  const [cornerSizeInPercent] = useState<number>(13);
  const { data: tiles, isLoading: isTilesLoading, isError: isTilesError } = useTiles();
  const { setBoardCenterPaddingX, setBoardCenterPaddingY } = useLayoutStore();

  useEffect(() => {
    const boardElement = document.getElementById("board");

    if (!boardElement) {
      return;
    }

    const boardWidth = boardElement.clientWidth - 12 - 12; // 12 px padding on each side
    const boardHeight = boardElement.clientHeight - 12 - 12; // 12 px padding on each side

    const gridCellWidth = (boardWidth * (100 - cornerSizeInPercent * 2)) / 100 / 9;
    const gridCellHeight = (boardHeight * (100 - cornerSizeInPercent * 2)) / 100 / 9;
    setGridCellWidth(gridCellWidth);
    setGridCellHeight(gridCellHeight);
    setBoardLoaded(true);

    setBoardCenterPaddingX(gridCellWidth + 12 + 12 + 6);
    setBoardCenterPaddingY(gridCellHeight + 12 + 12 + 6);
  }, [boardLoaded]);

  return (
    <BoardContext.Provider value={{ gridCellWidth, gridCellHeight, cornerSizeInPercent }}>
      <div className="aspect-square w-full">
        <div
          id="board"
          className="board relative h-full w-full p-3"
          style={{
            backgroundColor:
              // @ts-ignore
              window.Telegram.WebApp.themeParams.secondary_bg_color || "#334155",
          }}
        >
          {/* Generating tiles */}
          {boardLoaded && (
            <div id="tiles" className="relative h-full w-full">
              {!isTilesLoading &&
                !isTilesError &&
                tiles &&
                tiles.map((tile) => <BoardTile key={tile.position} tile={tile} />)}
            </div>
          )}
        </div>
      </div>
    </BoardContext.Provider>
  );
}

export default Board;
export { BoardContext };
