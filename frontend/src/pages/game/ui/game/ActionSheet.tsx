import { useGameStore } from "@/entities/gameStore";
import { useActionSheetConfig } from "@/shared/hooks/useActionSheetConfig";
import type React from "react";
import { useRef } from "react";
import { Sheet, type SheetRef } from "react-modal-sheet";

const snapPoints = [1, 0.15];

interface ActionSheetProps {
  // isOpen: boolean;
  // title: string | React.ReactNode;
  // hint: string | React.ReactNode;
  // actions: React.ReactNode[];
}

export const ActionSheet: React.FC<ActionSheetProps> = ({}) => {
  const ref = useRef<SheetRef>(null);
  const boardConfig = useGameStore((s) => s.boardConfig);
  const showActionSheet = useGameStore((s) => s.showActionSheet);

  const actionSheetCfg = useActionSheetConfig(boardConfig);
  if (!actionSheetCfg) {
    return null;
  }

  return (
    <Sheet
      ref={ref}
      isOpen={showActionSheet}
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
            <div className="flex flex-col gap-1">
              <h1 className="text-primary text-center text-2xl font-semibold">{actionSheetCfg.title}</h1>
              <p className="text-hint text-center whitespace-pre-wrap">{actionSheetCfg.hint}</p>
            </div>
            <div className="flex flex-col gap-2">{actionSheetCfg.actions}</div>
          </div>
        </Sheet.Content>
      </Sheet.Container>
      {/* <Sheet.Backdrop /> */}
    </Sheet>
  );
};
