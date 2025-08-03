import { Gamepad2Icon, PlusCircleIcon, StoreIcon, UsersRoundIcon } from "lucide-react";
import { motion, LayoutGroup, AnimatePresence } from "motion/react";
import { useState } from "react";
import { useHomeStore, type MenuTabs } from "../../stores/homeStore";

interface BottomNavProps {}

export const BottomNav = ({}: BottomNavProps) => {
  const [selected, setSelected] = useState(1);
  const menuTab = useHomeStore((s) => s.menuTab);
  const setMenuTab = useHomeStore((s) => s.setMenuTab);

  const handleMenuClick = (selectedIdx: number, menuTab: MenuTabs) => {
    setSelected(selectedIdx);
    setMenuTab(menuTab);
    Telegram.WebApp.HapticFeedback.impactOccurred("medium");
  };

  return (
    <LayoutGroup id="bottom-nav">
      <div className="mt-auto h-14 w-full shrink-0 py-2">
        <div className="bg-secondary-background relative grid h-full w-full grid-cols-3 rounded-full">
          <div
            className="relative -top-2 flex h-14 flex-col items-center justify-center rounded-full"
            onClick={() => handleMenuClick(0, "store")}
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
            className="relative -top-2 flex h-14 flex-col items-center justify-center rounded-full"
            onClick={() => {
              let newMenuTab: MenuTabs;

              switch (menuTab) {
                case "games": {
                  newMenuTab = "create_game";
                  break;
                }
                default: {
                  newMenuTab = "games";
                }
              }

              handleMenuClick(1, newMenuTab);
            }}
          >
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
            className="relative -top-2 flex h-14 flex-col items-center justify-center rounded-full"
            onClick={() => handleMenuClick(2, "friends")}
          >
            <UsersRoundIcon />
          </div>
        </div>
      </div>
    </LayoutGroup>
  );
};
