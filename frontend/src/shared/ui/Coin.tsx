import { cn } from "../utils";
import coin1 from "@/assets/coin1.png";
import coin2 from "@/assets/coin2.png";
import { COIN_FLIP_DURATION_MS } from "../config";
// import { COIN_FLIP_ANIMATION_DURATION_MS } from "@/config";

// const variants: Variants = {
//   disabled: { scale: 1 },
//   enabled: { scale: [1, 1.25, 1], transition: { duration: 0.3, ease: "easeOut" } },
// };

function Coin({
  disabled,
  rotation,
  onClick,
}: {
  disabled?: boolean;
  rotation: number;
  onClick?: () => void;
}) {
  // @ts-ignore
  //   const [rotation, setRotation] = useState(0);

  return (
    <div
      className={cn("relative aspect-square w-16 cursor-not-allowed rounded-full text-black", {
        "cursor-pointer outline-2 outline-offset-2 outline-amber-500": !disabled,
      })}
      style={{
        transform: `rotateY(${rotation}deg)`,
        // transform: `rotateY(${0}deg)`,
        transition: `transform ${COIN_FLIP_DURATION_MS / 1000}s ease-in-out, filter 100ms ease-in-out`,
        transformStyle: "preserve-3d",
        filter: disabled
          ? "brightness(0.5) drop-shadow(0 0 0.3rem #000)"
          : "brightness(1) drop-shadow(0 0 0.5rem #000)",
      }}
      onClick={onClick}
    >
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
    </div>
  );
}

export default Coin;
