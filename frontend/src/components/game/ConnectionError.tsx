import { cn } from "@/lib/utils";
import { useTheme } from "@/stores/ThemeContext";
import { SignalHighIcon, SignalLowIcon, SignalMediumIcon, SignalZeroIcon } from "lucide-react";
import { useEffect, useState } from "react";

interface SignalLowAnimationProps {
  size: number;
  color: string;
}

interface ConnectionErrorProps {
  show: boolean;
}

function SignalLowAnimation({ size = 20, color = "#fff" }: SignalLowAnimationProps) {
  const icons = [
    <SignalZeroIcon size={size} color={color} />,
    <SignalLowIcon size={size} color={color} />,
    <SignalMediumIcon size={size} color={color} />,
    <SignalHighIcon size={size} color={color} />,
  ];
  const [icon, setIcon] = useState(icons[0]);

  useEffect(() => {
    let index = 0;
    const interval = setInterval(() => {
      setIcon(icons[index]);
      index = (index + 1) % icons.length;
    }, 300);
    return () => clearInterval(interval);
  }, []);

  return <>{icon}</>;
}

function ConnectionError({ show }: ConnectionErrorProps) {
  const { textColor, destructiveTextColor } = useTheme();
  // const

  // if (!show) {
  //   return null;
  // }

  return (
    <div
      className={cn(
        "z-30 flex w-full items-center justify-center gap-4 opacity-90 transition-all duration-300 ease-in-out",
        show ? "h-8" : "h-0",
      )}
      style={{ backgroundColor: show ? destructiveTextColor : "green", color: textColor }}
    >
      <div className="flex items-center justify-center gap-2">
        <h1 className="tracking-widest">Connection error</h1>
        <div className="absolute right-2">
          <SignalLowAnimation size={20} color={textColor} />
        </div>
      </div>
    </div>
  );
}

export default ConnectionError;
