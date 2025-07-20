import React from "react";
import { cn } from "../utils";

interface SelectGroupProps {
  children?: React.ReactNode;
  defaultValue?: any;
  label?: string;
  id?: string;
  className?: string;
  disabled?: boolean;
  onChange: (value: any) => void;
}
interface SelectGroupItemProps {
  value: any;
  selected?: boolean;
  disabled?: boolean;
  onClick?: (value: any) => void;
  className?: string;
}

type SelectGroupComponent = React.FC<SelectGroupProps> & {
  Item: React.FC<SelectGroupItemProps>;
};

export const SelectGroup: SelectGroupComponent = ({
  label,
  id,
  defaultValue,
  className,
  disabled,
  onChange,
  children,
}) => {
  const [selectedValue, setSelectedValue] = React.useState<any>(defaultValue);

  return (
    <div className={cn("flex h-full w-full flex-col gap-2", className)}>
      <label
        htmlFor={id}
        className={cn({
          "text-hint": disabled,
        })}
      >
        {label}
      </label>
      <div role="radiogroup" id={id} className={cn("flex h-full w-full")}>
        {React.Children.map(children, (child) => {
          if (!React.isValidElement(child)) {
            return null;
          }

          const element = child as React.ReactElement<SelectGroupItemProps>;
          const { value } = element.props;
          const isSelected = value === selectedValue;
          return React.cloneElement(element, {
            selected: isSelected,
            disabled: disabled,
            onClick: () => {
              setSelectedValue(value);
              onChange(value);
            },
          });
        })}
      </div>
    </div>
  );
};

const SelectGroupItem: React.FC<SelectGroupItemProps> = ({
  value,
  selected,
  disabled,
  className,
  onClick,
}) => {
  return (
    <button
      role="radio"
      disabled={disabled}
      onClick={() => onClick!(value)}
      className={cn(
        "bg-background border-hint group relative flex h-full w-full items-center justify-center border-[1px] first:rounded-l-md last:rounded-r-md disabled:cursor-not-allowed disabled:opacity-50",
        className,
      )}
    >
      <div
        className={cn(
          "bg-link absolute top-0 left-0 z-0 h-full w-full transition-opacity duration-100 group-first:rounded-l-md group-last:rounded-r-md",
          {
            "opacity-100": selected,
            "opacity-0": !selected,
          },
        )}
      ></div>
      <p
        className={cn("z-10", {
          "text-button-text": selected,
          "text-primary": !selected,
        })}
      >
        {value}
      </p>
    </button>
  );
};

SelectGroup.Item = SelectGroupItem;
