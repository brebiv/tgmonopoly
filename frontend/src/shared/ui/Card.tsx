import type React from "react";
import cn from "classnames";

interface CardProps {
  className?: string;
  children: React.ReactNode;
}

export const Card: React.FC<CardProps> = ({ className, children }) => {
  return (
    <div
      className={cn(
        "text-2xl border-[1px] border-hint rounded-lg px-4 py-2 flex flex-col gap-4 relative bg-background [&_div]:bg-background",
        className
      )}
    >
      {children}
    </div>
  );
};
