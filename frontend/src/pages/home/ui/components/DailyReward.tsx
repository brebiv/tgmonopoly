import { Card } from "@/shared/ui/Card";
import { cn, getRandomArbitrary } from "@/shared/utils";

import checkmark from "@/assets/checkmark.png";
import coins from "@/assets/coins.png";
import { FancyJuicyButton } from "./FancyJuicyButton";

import { motion, useAnimationControls } from "motion/react";
import { CoinsController } from "./CoinsController";
import { useHomeStore, type HomeData, type StreakDay } from "../../stores/homeStore";
import { useEffect, useRef } from "react";
import { DailyRewardParticles } from "./DailyRewardParticles";
import { RippleEffect } from "./RippleEffect";

const data = {
  // streak: [
  //   { day: 1, status: "past", reward: 100, claimed: true },
  //   { day: 2, status: "past", reward: 200, claimed: true },
  //   { day: 3, status: "past", reward: 300, claimed: true },
  //   { day: 4, status: "present", reward: 400, claimed: false },
  //   { day: 5, status: "future", reward: 500, claimed: false },
  // ],
  // streak: [
  //   { day: 1, status: "present", reward: 100, claimed: false },
  //   { day: 2, status: "future", reward: 200, claimed: false },
  //   { day: 3, status: "future", reward: 300, claimed: false },
  //   { day: 4, status: "future", reward: 400, claimed: false },
  //   { day: 5, status: "future", reward: 500, claimed: false },
  // ],
  streak: [
    { day: 1, status: "past", reward: 100, claimed: true },
    { day: 2, status: "present", reward: 200, claimed: false },
    { day: 3, status: "future", reward: 300, claimed: false },
    { day: 4, status: "future", reward: 400, claimed: false },
    { day: 5, status: "future", reward: 500, claimed: false },
  ],
  coins: 1500,
};

const PastDay = ({ streakDay }: { streakDay: StreakDay }) => {
  const { reward, day, claimed } = streakDay;

  return (
    <motion.div className="bg-button border-button relative flex aspect-[9/15] w-full flex-col rounded-md border-1">
      <div
        className="z-10 flex h-full w-full flex-col rounded-md"
        style={{
          background: "linear-gradient(180deg,var(--color-accent-text) 0%, var(--color-button) 100%",
        }}
      >
        {/* Header */}
        <div
          className="flex h-4 w-full items-center rounded-t-md"
          style={{
            background: "linear-gradient(180deg,var(--color-accent-text) 0%, var(--color-button) 100%",
          }}
        >
          <p className="text-button-text w-full text-center text-xs">Day {day}</p>
        </div>

        {/* Body */}
        <div className="flex grow items-center justify-center">{claimed && <img src={checkmark} />}</div>

        {/* Footer */}
        <div className="bg-secondary-background mt-auto flex h-4 w-full items-center rounded-b-md">
          <p className="w-full text-center text-xs">+{reward}</p>
        </div>
      </div>
    </motion.div>
  );
};

const FutureDay = ({ streakDay }: { streakDay: StreakDay }) => {
  const { reward, day } = streakDay;

  return (
    <motion.div className="bg-button border-button relative flex aspect-[9/15] w-full flex-col rounded-md border-1">
      <div
        className="z-10 flex h-full w-full flex-col rounded-md"
        style={{
          background: "linear-gradient(180deg,var(--color-accent-text) 0%, var(--color-button) 100%",
        }}
      >
        {/* Header */}
        <div
          className="bg-secondary-background flex h-4 w-full items-center rounded-t-md"
          // style={{
          //   background: "linear-gradient(180deg,var(--color-accent-text) 0%, var(--color-button) 100%",
          // }}
        >
          <p className="w-full text-center text-xs">Day {day}</p>
        </div>

        {/* Body */}
        <div className="bg-secondary-background flex grow items-center justify-center">
          <img src={coins} />
        </div>

        {/* Footer */}
        <div className="bg-secondary-background mt-auto flex h-4 w-full items-center rounded-b-md">
          <p className="text-primary w-full text-center text-xs">+{reward}</p>
        </div>
      </div>
    </motion.div>
  );
};

const PresentDay = ({ streakDay }: { streakDay: StreakDay }) => {
  const { reward, day, claimed } = streakDay;
  const fireShaking = useHomeStore((s) => s.fireShaking);
  const setInTheMiddle = useHomeStore((s) => s.setInTheMiddle);

  const controls = useAnimationControls();
  const colorControls = useAnimationControls();
  const footerControls = useAnimationControls();
  const rotations = Array.from({ length: 20 }).map(() => `${getRandomArbitrary(-3, 3)}deg`);

  const firedHaptic = useRef<boolean>(false);

  useEffect(() => {
    if (!claimed) {
      colorControls.set({ backgroundColor: "var(--color-background)" });
      footerControls.set({ backgroundColor: Telegram.WebApp.themeParams.button_color });
      return;
    } else {
      if (!fireShaking) {
        colorControls.set({ backgroundColor: Telegram.WebApp.themeParams.button_color });
        footerControls.set({ backgroundColor: Telegram.WebApp.themeParams.button_color });
      }
    }

    if (fireShaking) {
      controls.start({
        scale: [1, 0.9, 1.1, 1],
        rotate: ["0deg", ...rotations, "0deg"],
      });
      colorControls.start({
        backgroundColor: claimed
          ? Telegram.WebApp.themeParams.button_color
          : Telegram.WebApp.themeParams.secondary_bg_color,
      });
    }
  }, [controls, claimed, fireShaking]);

  return (
    <motion.div
      id="current-day"
      className="bg-button outline-button-text relative flex aspect-[9/15] w-full flex-col rounded-md outline-2"
      animate={controls}
      onUpdate={(v) => {
        if ((v.scale as number) >= 1.05) {
          if (!firedHaptic.current) {
            Telegram.WebApp.HapticFeedback.impactOccurred("medium");
            firedHaptic.current = true;
            setInTheMiddle(true);
          }
        }
      }}
      transition={{ duration: 1, ease: "easeInOut", scale: { duration: 1, ease: "anticipate" } }}
    >
      <div
        className="z-10 flex h-full w-full flex-col rounded-md"
        style={{
          background: "linear-gradient(180deg,var(--color-accent-text) 0%, var(--color-button) 100%",
        }}
      >
        {/* Header */}
        <motion.div
          className={cn("flex h-4 w-full items-center rounded-t-md", {
            // "bg-secondary-background": !claimed,
          })}
          animate={colorControls}
        >
          <p
            className={cn("text-button-text w-full text-center text-xs", {
              "text-current": !claimed,
            })}
          >
            Day {day}
          </p>
        </motion.div>

        {/* Body */}
        <motion.div
          layout
          animate={colorControls}
          // initial={{ backgroundColor: "var(--color-background)" }}
          className="flex grow items-center justify-center"
        >
          {!claimed && (
            <motion.img
              animate={{ rotate: [5, -5, 5], scale: [1, 1.05, 1] }}
              transition={{ duration: 1.3, repeat: Infinity, ease: "linear" }}
              src={coins}
            />
          )}
          {claimed && <img src={checkmark} />}
        </motion.div>

        {/* Footer */}
        <motion.div className="mt-auto flex h-4 w-full items-center rounded-b-md" animate={footerControls}>
          <p className="text-button-text w-full text-center text-xs">+{reward}</p>
        </motion.div>
      </div>

      {/* Shining */}
      <div className="absolute z-10 h-full w-full overflow-hidden">
        <motion.div
          initial={{ bottom: "-200%", left: "-200%" }}
          animate={{ bottom: "200%", left: "200%" }}
          transition={{ duration: 1.5, repeat: Infinity, repeatDelay: 3, delay: 1 }}
          className="absolute z-10 h-[200%] w-[200%] rotate-45"
          style={{
            background:
              "linear-gradient(to bottom, rgba(229, 172, 142, 0), rgba(255,255,255,0.5) 50%, rgba(229, 172, 142, 0))",
          }}
        ></motion.div>
      </div>
    </motion.div>
  );
};

interface DailyRewardProps {}
export const DailyReward = ({}: DailyRewardProps) => {
  const streak = useHomeStore((s) => s.streak);
  const initHomeData = useHomeStore((s) => s.initHomeData);
  const claimCurrentDay = useHomeStore((s) => s.claimCurrentDay);

  useEffect(() => {
    initHomeData(data as HomeData);
  }, []);

  return (
    <>
      <RippleEffect />
      <CoinsController />
      <Card
        className="relative pb-3"
        style={{
          background:
            "linear-gradient(0deg,var(--color-secondary-background) 00%, var(--color-accent-text) 100%",
        }}
      >
        <DailyRewardParticles />
        <div id="gameCard" className="flex flex-col items-center gap-4">
          <h1 className="text-button-text text-lin z-10 uppercase">Daily reward</h1>
          <div className="grid h-full w-full grid-cols-5 gap-2">
            {streak &&
              streak.map((day) => {
                switch (day.status) {
                  case "past": {
                    return <PastDay key={day.day} streakDay={day} />;
                  }
                  case "present": {
                    return <PresentDay key={day.day} streakDay={day} />;
                  }
                  case "future": {
                    return <FutureDay key={day.day} streakDay={day} />;
                  }
                }
              })}
          </div>
          <div className="w-full">
            <FancyJuicyButton
              className="w-full"
              onClick={() => {
                claimCurrentDay();
              }}
            >
              Claim
            </FancyJuicyButton>
          </div>
        </div>
      </Card>
    </>
  );
};
