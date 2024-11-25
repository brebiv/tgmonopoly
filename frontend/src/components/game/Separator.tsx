import { cn } from "@/lib/utils";
import { useTheme } from "@/stores/ThemeContext";

function Separator({ orientation = "horizontal" }: { orientation?: "vertical" | "horizontal" }) {
  const { sectionSeparatorColor } = useTheme();
  return (
    <div
      className={cn(orientation === "vertical" ? "h-full w-[2px]" : "h-[2px] w-full")}
      style={{ backgroundColor: sectionSeparatorColor }}
    />
  );
}

export default Separator;
