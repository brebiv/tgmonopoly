import React from "react";
import { motion } from "motion/react";
import { cn } from "../utils";

interface ButtonProps {
  children?: React.ReactNode;
  className?: string;
  disabled?: boolean;
  onClick?: (...args: any[]) => void;
}

export const Button: React.FC<ButtonProps> = ({ children, className, disabled = false, ...props }) => {
  return (
    <motion.button
      disabled={disabled}
      className={cn(
        "flex items-center justify-center rounded-full px-2 py-1",
        "disabled:cursor-not-allowed disabled:opacity-50",
        className,
      )}
      whileTap={{ scale: 0.95 }}
      {...props}
    >
      {children ? children : "Button"}
    </motion.button>
  );
};
