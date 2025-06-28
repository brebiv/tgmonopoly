import React from "react";
import cn from "classnames";

interface ButtonProps {
  children: React.ReactNode;
  className?: string;
  onClick: (...args: any[]) => void;
}

export const Button: React.FC<ButtonProps> = ({
  children,
  className,
  ...props
}) => {
  return (
    <button
      className={cn(
        "rounded-lg px-2 py-1 flex items-center justify-center",
        className
      )}
      {...props}
    >
      {children}
    </button>
  );
};
