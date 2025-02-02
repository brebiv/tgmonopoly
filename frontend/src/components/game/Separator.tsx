import { cn } from "@/lib/utils";
import { useTheme } from "@/stores/ThemeContext";

function Separator({
  orientation = "horizontal",
  className,
  style,
}: {
  orientation?: "vertical" | "horizontal";
  className?: string;
  style?: React.CSSProperties;
}) {
  const { sectionSeparatorColor } = useTheme();
  return (
    <div
      className={cn(orientation === "vertical" ? "h-full w-[2px]" : "h-[2px] w-full", className)}
      style={{ backgroundColor: sectionSeparatorColor, ...style }}
    />
  );
}

export default Separator;
