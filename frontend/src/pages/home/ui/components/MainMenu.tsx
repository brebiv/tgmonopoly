import { Button } from "@/shared/ui/Button";
import { Shining } from "@/shared/ui/Shining";
import { Gamepad2Icon, PlusIcon, SettingsIcon, UsersRoundIcon } from "lucide-react";

export const MainMenu = () => {
  return (
    <div className="flex w-full grow flex-col gap-6 pb-4">
      {/* System status header */}
      {/* <div className="flex">
        <div className="flex gap-2">
          <div className="flex gap-1">
            <UsersRoundIcon /> 7k
          </div>
          <div className="flex gap-1">
            <Gamepad2Icon /> 532
          </div>
        </div>
      </div> */}

      {/* Buttons */}
      {/* <div className="mt-auto flex w-full flex-col items-center gap-4"> */}
      <div className="relative mt-auto flex gap-8">
        <div className="relative flex grow-0 items-center justify-start">
          <Button className="flex gap-1 rounded-xl p-4 text-xl font-extrabold">
            <SettingsIcon />
          </Button>
        </div>
        <div className="relative bottom-4 flex shrink-0 grow-3">
          <Button className="flex w-full gap-1 rounded-xl p-4 text-xl font-extrabold">Play</Button>
          <div className="pointer-events-none absolute h-full w-full rounded-xl">
            <Shining />
          </div>
        </div>
        <div className="relative flex items-center justify-end">
          <Button className="flex gap-1 rounded-xl p-4 text-xl font-extrabold">
            <PlusIcon />
          </Button>
        </div>
        {/* <Button className="flex w-1/2 gap-1 p-4 font-medium">
          <Gamepad2Icon />
          Create lobby
        </Button> */}

        {/* <div className="w-fulll mt-auto flex items-center justify-center">
          <Button>Quick Join</Button>
        </div> */}
      </div>
    </div>
  );
};
