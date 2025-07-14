import type React from "react";
import { useRef } from "react";
import { Sheet, type SheetRef } from "react-modal-sheet";

const snapPoints = [1, 0.2];

interface ActionSheetProps {
  isOpen: boolean;
  title: string | React.ReactNode;
  hint: string | React.ReactNode;
  actions: React.ReactNode[];
}

export const ActionSheet: React.FC<ActionSheetProps> = ({ isOpen, title, hint, actions }) => {
  const ref = useRef<SheetRef>(null);

  return (
    <Sheet
      ref={ref}
      isOpen={isOpen}
      onClose={() => {}}
      detent={"content-height"}
      snapPoints={snapPoints}
      dragCloseThreshold={1} // makes it unclosable
      dragVelocityThreshold={9999} // makes it unclosable
    >
      <Sheet.Container>
        <Sheet.Header className="bg-background rounded-t-lg" />
        <Sheet.Content className="bg-background">
          <div className="flex flex-col gap-4 px-4 pb-12">
            <div className="flex flex-col">
              <h1 className="text-primary text-center text-2xl font-semibold">{title}</h1>
              <p className="text-hint text-center whitespace-pre-wrap">{hint}</p>
            </div>
            <div className="flex flex-col gap-2">
              {/* <RollDiceButton /> */}
              {actions}
            </div>
          </div>
        </Sheet.Content>
      </Sheet.Container>
      {/* <Sheet.Backdrop /> */}
    </Sheet>
  );
};
