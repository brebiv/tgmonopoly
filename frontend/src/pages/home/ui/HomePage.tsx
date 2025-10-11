import { Header } from "./components/Header";
import { BottomNav } from "./components/BottomNav";
import { MenuContent } from "./MenuContent";
// import { useEffect } from "react";

export const HomePage = () => {
  // useEffect(() => {
  //   Telegram.WebApp.requestFullscreen();
  // }, []);

  return (
    // <div className="bg-background relative flex h-screen w-full flex-col gap-4 px-4 pt-4 pb-6">
    <div
      className="bg-background relative grid h-screen w-full grid-cols-2 px-4 pt-4 pb-6"
      style={{ gridTemplateRows: "repeat(16, minmax(0, 1fr))" }}
    >
      <div className="col-span-2 row-span-1">
        <Header />
      </div>
      <div className="col-span-2 row-span-15">
        <MenuContent />
      </div>
      <div className="col-span-2 -row-start-1">
        <BottomNav />
      </div>
    </div>
  );
};
