import Confetti from "react-confetti-boom";
import { useEffect, useState } from "react";
import { useGameStore } from "@/entities/gameStore";

interface ConfettiControllerProps {
  // fire?: boolean;
  keepAlive?: number;
}

export const ConfettiController = ({ keepAlive = 2500 }: ConfettiControllerProps) => {
  const [visible, setVisible] = useState(false);
  const [fire, setFire] = useState(false);

  const myPlayer = useGameStore((s) => s.myPlayer);
  const isWonCasino = useGameStore((s) => s.isWonCasino);
  const casinoPlayer = useGameStore((s) => s.casinoPlayer);

  useEffect(() => {
    if (isWonCasino && casinoPlayer && myPlayer && casinoPlayer.id == myPlayer.id) {
      setFire(true);
    } else {
      setFire(false);
    }
  }, [myPlayer, isWonCasino, casinoPlayer]);

  useEffect(() => {
    if (fire) setVisible(true);
  }, [fire]);

  useEffect(() => {
    if (!fire && visible) {
      const id = window.setTimeout(() => setVisible(false), keepAlive);
      return () => clearTimeout(id);
    }
  }, [fire, visible, keepAlive]);

  return (
    visible && (
      <div className="fixed top-0 z-30 h-full w-full">
        <Confetti
          y={0.6}
          shapeSize={10}
          launchSpeed={1.4}
          particleCount={140}
          //   effectCount={1000}
          effectInterval={keepAlive + 1}
          colors={[
            Telegram.WebApp.themeParams.accent_text_color || "",
            Telegram.WebApp.themeParams.button_color || "",
            Telegram.WebApp.themeParams.text_color,
            // Telegram.WebApp.themeParams.destructive_text_color || "",
          ]}
        />
      </div>
    )
  );
};
