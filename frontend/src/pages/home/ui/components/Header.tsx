import { PlusIcon } from "lucide-react";
import coin from "@/assets/coin.png";

export const Header = () => {
  return (
    <header className="text-primary grid w-full shrink-0 grid-cols-3">
      <div className="bg-secondary-background col-start-3 flex rounded-md p-1">
        <div>
          <PlusIcon />
        </div>
        <div className="ml-auto flex items-center gap-1">
          <p className="text-sm">1500</p>
          <img className="w-6" src={coin} />
        </div>
      </div>
    </header>
  );
};
