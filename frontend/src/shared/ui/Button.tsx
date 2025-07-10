import React from "react";
import cn from "classnames";

interface ButtonProps {
  children?: React.ReactNode;
  className?: string;
  disabled?: boolean;
  onClick?: (...args: any[]) => void;
}

export const Button: React.FC<ButtonProps> = ({ children, className, disabled = false, ...props }) => {
  return (
    <button
      disabled={disabled}
      className={cn(
        "flex items-center justify-center rounded-lg px-2 py-1",
        "disabled:cursor-not-allowed disabled:opacity-50",
        className,
      )}
      {...props}
    >
      {children ? children : "Button"}
    </button>
  );
};
