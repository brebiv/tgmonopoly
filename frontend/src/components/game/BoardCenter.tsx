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
      <div className="relative h-full w-full">{children}</div>
    </div>
  );
}

export default BoardCenter;
