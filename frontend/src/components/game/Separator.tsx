import { useTheme } from "@/stores/ThemeContext";

function Separator() {
  const { sectionSeparatorColor } = useTheme();
  return <div className="h-[2px] w-full" style={{ backgroundColor: sectionSeparatorColor }} />;
}

export default Separator;
