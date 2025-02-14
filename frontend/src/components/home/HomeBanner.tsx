import { useTheme } from "@/stores/ThemeContext";

function HomeBanner() {
  const { bgColor } = useTheme();
  return (
    <div className="flex h-40 w-full flex-col gap-4">
      <h1 className="text-center">Welcome back!</h1>
      <div className="flex h-16 items-center gap-2">
        {Array.from({ length: 5 }).map((_, i) => (
          <div
            key={i}
            className="h-full flex-1 animate-pulse rounded-sm"
            style={{ backgroundColor: bgColor }}
          ></div>
        ))}
      </div>
    </div>
  );
}

export default HomeBanner;
