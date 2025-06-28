import React from "react";
import cn from "classnames";

interface NavButtonProps {
  text: string;
  active?: boolean;
  disabled?: boolean;
  onClick: () => void;
  className?: string;
}

export const NavButton: React.FC<NavButtonProps> = ({
  text,
  active,
  onClick,
  className = "",
  disabled = false,
  ...props
}) => {
  return (
    <button
      onClick={() => {
        if (!disabled) onClick();
      }}
      className={cn(
        "relative border-[1px] bg-transparent border-hint rounded-lg px-2 py-1 flex justify-center focus:outline-none",
        className
      )}
      {...props}
    >
      <div
        className={cn(
          "absolute w-full h-full left-0 top-0 rounded-lg transition-opacity duration-75",
          {
            "opacity-20": active && !disabled,
            "opacity-0": !active,
            "bg-link": !disabled,
            "opacity-50": disabled,
            "bg-secondary-background": disabled,
          }
        )}
      ></div>
      <p
        className={cn("transition-color duration-75", {
          "text-link": active,
          "text-hint": disabled,
        })}
      >
        {text}
      </p>
    </button>
  );
};
