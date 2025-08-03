import { PlusIcon } from "lucide-react";
import coin from "@/assets/coin.png";
import { useHomeStore } from "../../stores/homeStore";

import { useEffect, useRef, useState } from "react";
import { animate, useMotionValue, motion, useAnimationControls } from "motion/react";
import { cn } from "@/shared/utils";

export function Counter({
  value,
  duration = 0.15,
  decimals = 1,
}: {
  value: number;
  duration?: number;
  decimals?: number;
}) {
  const nodeRef = useRef(null);
  const mv = useMotionValue(value);
  const controlsRef = useRef(null);
  const prevRef = useRef(value);
  const controls = useAnimationControls();
  const [skipAnimation, setSkipAnimation] = useState(false);

  useEffect(() => {
    if (nodeRef.current) {
      // @ts-ignore
      nodeRef.current.textContent = Number(mv.get()).toFixed(decimals);
    }
    const unsub = mv.on("change", (v) => {
      // @ts-ignore
      if (nodeRef.current) nodeRef.current.textContent = v.toFixed(decimals);
      if (!skipAnimation) {
        controls.start({
          scale: [1, 1.1, 1],
        });
      }
    });
    return unsub;
  }, [decimals, mv, skipAnimation]);

  useEffect(() => {
    const prev = prevRef.current;
    prevRef.current = value;
    // @ts-ignore
    controlsRef.current?.stop();

    if (prev == 0) {
      mv.set(value);
      setSkipAnimation(true);
      return;
    }
    setSkipAnimation(false);

    // @ts-ignore
    controlsRef.current = animate(mv, value, {
      duration,
    });

    // @ts-ignore
    return () => controlsRef.current?.stop();
  }, [value, duration, mv]);

  return <motion.p ref={nodeRef} initial={false} animate={controls} transition={{ duration: 0.25 }} />;
}

const CoinsSection = () => {
  const coins = useHomeStore((s) => s.coins);
  const coinsFinishCount = useHomeStore((s) => s.coinsFinishCount);

  const coinsDivControls = useAnimationControls();
  const coinControls = useAnimationControls();

  useEffect(() => {
    if (coinsFinishCount == 0) return;

    coinsDivControls.start({
      outlineWidth: ["0px", "3px", "0px"],
    });
    coinControls.start({
      scale: [1, 1.1, 1],
    });
  }, [coinsFinishCount, coinsDivControls]);
  return (
    <motion.div
      animate={coinsDivControls}
      transition={{ duration: 0.3 }}
      className={cn(
        "bg-secondary-background col-start-3 flex items-center rounded-md px-1 outline-0 outline-yellow-500",
      )}
    >
      <div>
        <PlusIcon />
      </div>
      <div className="ml-auto flex items-center gap-1">
        {/* <CoinsController /> */}
        <Counter value={coins} decimals={0} />
        <motion.img id="header-coin" className="w-8" src={coin} animate={coinControls} />
      </div>
    </motion.div>
  );
};

export const Header = () => {
  return (
    <header className="text-primary grid w-full shrink-0 grid-cols-3">
      <CoinsSection />
    </header>
  );
};
