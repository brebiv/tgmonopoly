import { useTheme } from "@/stores/ThemeContext";

function ThemedDiv({ className, children }: { className?: string; children: React.ReactNode }) {
  const { textColor, bgColor } = useTheme();
  return (
    <div
      className={className}
      style={{
        backgroundColor: bgColor,
        color: textColor,
      }}
    >
      {children}
    </div>
  );
}

export default ThemedDiv;
