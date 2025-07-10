import { Button } from "@/shared/ui/Button";
import { DicesIcon } from "lucide-react";
import type React from "react";

export const RollDiceButton: React.FC = () => {
  return (
    <Button className="flex gap-2 py-3 text-lg font-semibold">
      <DicesIcon /> {"Roll dice"}
    </Button>
  );
};
