import { useEffect } from "react";
import coin1 from "@/assets/coin1.png";
import coin2 from "@/assets/coin2.png";
import { cn } from "@/lib/utils";
import { useGameStore } from "@/stores/GameStore";
import { COIN_FLIP_ANIMATION_DURATION_MS } from "@/config";

function Coin({ disabled, onClick }: { disabled: boolean; onClick?: () => void }) {
  const { coinRotation: rotation } = useGameStore((state) => state);

  useEffect(() => {
    console.log("rotation", rotation);
  }, [rotation]);

  return (
    <div
      className={cn("relative aspect-square w-16 rounded-full text-black", {
        "outline outline-2 outline-offset-2 outline-amber-500": !disabled,
      })}
      style={{
        transform: `rotateY(${rotation}deg)`,
        transition: `transform ${COIN_FLIP_ANIMATION_DURATION_MS / 1000}s ease-in-out, filter 100ms ease-in-out`,
        transformStyle: "preserve-3d",
        filter: disabled
          ? "brightness(0.5) drop-shadow(0 0 0.3rem #000)"
          : "brightness(1) drop-shadow(0 0 0.5rem #000)",
        cursor: disabled ? "not-allowed" : "pointer",
      }}
      onClick={onClick}
    >
      <>
        <img
          src={coin1}
          className={cn("absolute h-full w-full", {
            "custom-ping": !disabled,
          })}
          alt="coin_side_1"
        />
        <img
          src={coin2}
          className={cn("absolute h-full w-full", {
            "custom-ping": !disabled,
          })}
          alt="coin_side_2"
          style={{ transform: `translateZ(1px)` }}
        />
      </>
    </div>
  );
}

export default Coin;
