import { Header } from "./components/Header";
import { BottomNav } from "./components/BottomNav";
import { MenuContent } from "./MenuContent";

export const HomePage = () => {
  return (
    <div className="bg-background relative flex h-screen w-full flex-col gap-4 px-4 pt-4 pb-6">
      <Header />
      <MenuContent />
      <BottomNav />
    </div>
  );
};
