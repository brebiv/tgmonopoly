// import DisplacementMap from "@/assets/DisplacementMap.png";
import { motion, useAnimationControls } from "motion/react";
import { useEffect } from "react";
import { useHomeStore } from "../../stores/homeStore";

export const RippleEffect = () => {
  const inTheMiddle = useHomeStore((s) => s.inTheMiddle);
  const controls = useAnimationControls();

  useEffect(() => {
    if (!inTheMiddle) return;
    if (import.meta.env.VITE_DISABLE_SVG_FILTERS_IN_SAFARI == true && (window as any).safari) return;

    document.body.style.filter = "url(#filters-noise)";
    controls.start(
      { baseFrequency: ["0 0", `${0.01} ${0.01}`, "0 0"] },
      {
        duration: 0.7,
        onComplete: () => {
          document.body.style.filter = "";
        },
      },
    );
  }, [inTheMiddle]);

  return (
    <svg width="0" height="0">
      <defs>
        <filter id="filters-noise" x="0%" y="0%" width="150%" height="150%">
          <motion.feTurbulence
            initial={false}
            animate={controls}
            numOctaves="1"
            type={"fractalNoise"}
            result="noise"
          ></motion.feTurbulence>
          <feDisplacementMap
            in="SourceGraphic"
            in2="noise"
            scale="10"
            xChannelSelector="R"
            yChannelSelector="R"
            result="out"
          ></feDisplacementMap>
        </filter>
      </defs>
    </svg>
  );
};
