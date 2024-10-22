// @ts-nocheck
import { hexToRGBA } from "@/lib/utils";
import { useLayoutStore } from "@/stores/LayoutStore";

function BoardCenter({ children }: { children: React.ReactNode }) {
  const { boardCenterPaddingX, boardCenterPaddingY } = useLayoutStore();

  return (
    <div
      className="absolute z-10 aspect-square w-full"
      style={{
        padding: `${boardCenterPaddingY}px ${boardCenterPaddingX}px`,
        paddingBottom: `${boardCenterPaddingY + 4}px`,
      }}
    >
      <div className="relative h-full w-full">
        <div
          className="absolute z-10 h-2 w-full"
          style={{
            backgroundImage: `linear-gradient(
          180deg,
          ${window.Telegram.WebApp.themeParams.secondary_bg_color || "rgb(18, 17, 19)"} -10%,
          ${hexToRGBA(window.Telegram.WebApp.themeParams.secondary_bg_color, 0) || "rgb(18, 17, 19, 0)"} 110%)`,
          }}
        ></div>
        {children}
        <div
          className="absolute bottom-0 z-10 h-2 w-full"
          style={{
            backgroundImage: `linear-gradient(
          0deg,
          ${window.Telegram.WebApp.themeParams.secondary_bg_color || "rgb(18, 17, 19)"} -10%,
          ${hexToRGBA(window.Telegram.WebApp.themeParams.secondary_bg_color, 0) || "rgb(18, 17, 19, 0)"} 110%)`,
          }}
        ></div>
      </div>
    </div>
  );
}

export default BoardCenter;
