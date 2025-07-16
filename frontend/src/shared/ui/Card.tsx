import type React from "react";
import { cn } from "../utils";

interface CardProps {
  className?: string;
  children: React.ReactNode;
}

export const Card: React.FC<CardProps> = ({ className, children }) => {
  return (
    <div
      className={cn(
        "border-hint bg-background [&_div]:bg-background relative flex flex-col gap-4 rounded-lg border-[1px] px-4 py-2 text-2xl",
        className,
      )}
    >
      {children}
    </div>
  );
};
