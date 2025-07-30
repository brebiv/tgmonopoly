import { cn } from "@/shared/utils";
import { Gamepad2Icon, PlusCircleIcon, StoreIcon, UsersRoundIcon } from "lucide-react";
import { motion, LayoutGroup, AnimatePresence } from "motion/react";
import { useState } from "react";
import { useHomeStore } from "../../stores/homeStore";

interface BottomNavProps {}

export const BottomNav = ({}: BottomNavProps) => {
  const [selected, setSelected] = useState(1);
  const menuTab = useHomeStore((s) => s.menuTab);
  const setMenuTab = useHomeStore((s) => s.setMenuTab);

  return (
    <LayoutGroup id="bottom-nav">
      {/* <div className="fixed bottom-6 left-0 h-14 w-full px-8 py-2"> */}
      <div className="mt-auto h-14 w-full shrink-0 py-2">
        <div className="bg-secondary-background relative grid h-full w-full grid-cols-3 rounded-full">
          <div
            className={cn("relative -top-2 flex h-14 flex-col items-center justify-center rounded-full", {
              // "bg-button h-14": selected == 1,
            })}
            onClick={() => {
              setSelected(0);
              setMenuTab("store");
            }}
          >
            {/* Selection pill */}
            <motion.div
              layout
              layoutId="nav-pill"
              className="bg-button absolute h-14 w-full rounded-full"
              style={{ left: `${100 * selected}%` }}
              transition={{ type: "spring", stiffness: 200, damping: 20 }}
            ></motion.div>
            <StoreIcon className="z-10" />
          </div>
          <div
            className={cn("relative -top-2 flex h-14 flex-col items-center justify-center rounded-full", {
              // "bg-button h-14": selected == 2,
            })}
            onClick={() => {
              switch (menuTab) {
                case "games": {
                  setMenuTab("create_game");
                  break;
                }
                default: {
                  setMenuTab("games");
                }
              }

              setSelected(1);
            }}
          >
            {/* <p className="text-button-text">New game</p> */}
            <motion.p layout="position" className="text-button-text flex flex-col items-center">
              <AnimatePresence mode="wait" initial={false}>
                {menuTab === "games" ? (
                  <motion.span
                    key="new"
                    initial={{ opacity: 0, y: 4 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -4 }}
                    transition={{ duration: 0.1 }}
                    className="flex flex-col items-center"
                  >
                    <PlusCircleIcon />
                    New game
                  </motion.span>
                ) : menuTab === "create_game" ? (
                  <motion.span
                    key="games"
                    initial={{ opacity: 0, y: 4 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -4 }}
                    transition={{ duration: 0.1 }}
                    className="flex flex-col items-center justify-center text-center"
                  >
                    Cancel
                  </motion.span>
                ) : (
                  <motion.span
                    key="games"
                    initial={{ opacity: 0, y: 4 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -4 }}
                    transition={{ duration: 0.1 }}
                    className="inline-flex items-center"
                  >
                    <Gamepad2Icon />
                  </motion.span>
                )}
              </AnimatePresence>
            </motion.p>
          </div>
          <div
            className={cn("relative -top-2 flex h-14 flex-col items-center justify-center rounded-full", {
              // "bg-button h-14": selected == 3,
            })}
            onClick={() => {
              setSelected(2);
              setMenuTab("friends");
            }}
          >
            <UsersRoundIcon />
          </div>
        </div>
      </div>
    </LayoutGroup>
  );
};
