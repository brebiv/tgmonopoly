import coin from "@/assets/coin.png";
import { generateScatteredPointsFromElement, getRandomArbitrary } from "@/shared/utils";

import { LayoutGroup, motion, type Point } from "motion/react";
import { useEffect, useState } from "react";
import { useHomeStore } from "../../stores/homeStore";
import Confetti from "react-confetti-boom";

const DailyRewardConffetiController = ({ fire }: { fire: boolean }) => {
  const [visible, setVisible] = useState(false);

  const keepAlive = 3000;

  useEffect(() => {
    if (fire) setVisible(true);
  }, [fire]);

  useEffect(() => {
    if (!fire && visible) {
      const id = window.setTimeout(() => setVisible(false), keepAlive);
      return () => clearTimeout(id);
    }
  }, [fire, visible, keepAlive]);

  if (visible) {
    return <Confetti className="z-30" y={0.3} />;
  }
};

interface CoinsControllerProps {}

type PointWithDuration = {
  duration: number;
} & Point;

export const CoinsController = ({}: CoinsControllerProps) => {
  const [positions, setPostions] = useState<PointWithDuration[]>([]);
  const [centerPoint, setCenterPoint] = useState<Point>({ x: 0, y: 0 });
  const [targetPoint, setTargetPoint] = useState<Point>({ x: 0, y: 0 });

  const fireCoins = useHomeStore((s) => s.fireCoins);
  const coinsCount = useHomeStore((s) => s.coinsCount);
  const handleCoinFinished = useHomeStore((s) => s.handleCoinFinished);

  const handleFire = () => {
    const elem = document.getElementById("current-day");
    const targetElem = document.getElementById("header-coin");
    if (!elem || !targetElem) throw new Error("Could not find sourse or start elements for coins");

    const points = generateScatteredPointsFromElement(elem, { count: coinsCount, scale: 1, seed: 4 });
    const pointsWithDuration = points.map((p) =>
      Object.assign(p, { duration: getRandomArbitrary(0.8, 1.8) }),
    );

    const rect = elem.getBoundingClientRect();
    const center = {
      x: rect.left + rect.width / 2 - 32 / 2,
      y: rect.top + rect.height / 2 - 32 / 2,
    };
    const targetRect = targetElem.getBoundingClientRect();
    const targetCenter = {
      x: targetRect.left + targetRect.width / 2 - 32 / 2,
      y: targetRect.top + targetRect.height / 2 - 32 / 2,
    };

    setCenterPoint(center);
    setPostions(pointsWithDuration);
    setTargetPoint(targetCenter);
  };

  useEffect(() => {
    if (fireCoins) {
      handleFire();
    }
  }, [fireCoins]);

  return (
    <div id="coins" className="pointer-events-none absolute top-0 left-0 z-20 h-screen w-screen">
      <DailyRewardConffetiController fire={fireCoins} />
      <LayoutGroup id="coins">
        {fireCoins && (
          <>
            {positions.map((p, i) => (
              <motion.img
                key={i}
                className="absolute z-20 w-8"
                src={coin}
                transition={{
                  ease: "anticipate",
                  // ease: "easeInOut",
                  duration: p.duration,
                  // opacity: { ease: "linear", duration: 0.01, delay: 0.3 },
                  // opacity: { ease: "easeIn", duration: 1, delay: p.duration / 2 },
                }}
                initial={{ left: `${centerPoint.x}px`, top: `${centerPoint.y}px` }}
                animate={{
                  left: [`${centerPoint.x}px`, `${p.x}px`, `${targetPoint.x}px`],
                  top: [`${centerPoint.y}px`, `${p.y}px`, `${targetPoint.y}px`],
                  // opacity: [0, 1],
                }}
                onAnimationComplete={() => {
                  handleCoinFinished();
                  Telegram.WebApp.HapticFeedback.impactOccurred("light");
                }}
              />
            ))}
          </>
        )}
      </LayoutGroup>
    </div>
  );
};
