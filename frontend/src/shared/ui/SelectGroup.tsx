import React from "react";
import cn from "classnames";

interface SelectGroupProps {
  children?: React.ReactNode;
  defaultValue?: any;
  onChange: (value: any) => void;
}
interface SelectGroupItemProps {
  value: any;
  selected?: boolean;
  onClick?: (value: any) => void;
}

type SelectGroupComponent = React.FC<SelectGroupProps> & {
  Item: React.FC<SelectGroupItemProps>;
};

export const SelectGroup: SelectGroupComponent = ({
  children,
  defaultValue,
  onChange,
}) => {
  const [selectedValue, setSelectedValue] = React.useState<any>(defaultValue);

  return (
    <div role="radiogroup" className="flex">
      {React.Children.map(children, (child) => {
        if (!React.isValidElement(child)) {
          return null;
        }

        const element = child as React.ReactElement<SelectGroupItemProps>;
        const { value } = element.props;
        const isSelected = value === selectedValue;
        return React.cloneElement(element, {
          selected: isSelected,
          onClick: () => {
            setSelectedValue(value);
            onChange(value);
          },
        });
      })}
    </div>
  );
};

const SelectGroupItem: React.FC<SelectGroupItemProps> = ({
  value,
  selected,
  onClick,
}) => {
  return (
    <button
      role="radio"
      onClick={() => onClick!(value)}
      className={cn(
        "relative w-10 h-10 bg-background border-[1px] flex items-center justify-center border-hint first:rounded-l-md last:rounded-r-md group"
      )}
    >
      <div
        className={cn(
          "absolute bg-link z-0 w-full h-full left-0 top-0 transition-opacity duration-100 group-first:rounded-l-md group-last:rounded-r-md",
          {
            "opacity-100": selected,
            "opacity-0": !selected,
          }
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
