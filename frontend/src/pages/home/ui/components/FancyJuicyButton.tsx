import React, { useState } from "react";
import cn from "classnames";
import Confetti from "react-confetti-boom";
import { motion } from "motion/react";

interface ButtonProps {
  children?: React.ReactNode;
  className?: string;
  disabled?: boolean;
  fireConfetti?: boolean;
  onClick?: () => void;
}

export const FancyJuicyButton: React.FC<ButtonProps> = ({
  children,
  className,
  disabled = false,
  fireConfetti = false,
  onClick,
  ...props
}) => {
  const [fire, setFire] = useState(false);

  return (
    <>
      {fire && (
        <Confetti
          y={0.6}
          shapeSize={10}
          launchSpeed={1.4}
          particleCount={140}
          //   effectCount={1000}
          effectInterval={2500}
          colors={[
            Telegram.WebApp.themeParams.accent_text_color || "",
            Telegram.WebApp.themeParams.button_color || "",
            Telegram.WebApp.themeParams.text_color,
            // Telegram.WebApp.themeParams.destructive_text_color || "",
          ]}
          className="absolute z-100"
        />
      )}
      <motion.button
        disabled={disabled}
        className={cn(
          "flex items-center justify-center rounded-full px-2 py-1",
          "disabled:cursor-not-allowed disabled:opacity-50",
          "from-accent-text to-button bg-linear-to-b",
          // "outline-button outline-2",
          "relative overflow-hidden",
          className,
        )}
        // initial={{scale:}}
        animate={{ scale: [0.95, 1.05, 1] }}
        transition={{
          duration: 0.3,
          // times: [0, 0.35, 1], // optional: timing of each keyframe
          ease: "easeOut", // optional
        }}
        whileTap={{ scale: 0.95 }}
        onClick={() => {
          Telegram.WebApp.HapticFeedback.impactOccurred("heavy");
          if (onClick) {
            onClick();
          }
          if (fireConfetti) {
            setFire(true);
          }
        }}
        {...props}
      >
        {/* <motion.div
          className="absolute top-0 left-0 h-8 w-8 bg-black"
          style={{
            // Follow a rounded-rectangle that matches the button’s border radius
            // `inset(0 round <radius>)` draws a rounded-rect along the element’s border-box
            offsetPath: `inset(0 round 9999px)`,
            // Make the image rotate to face the direction of travel; remove if not desired
            offsetRotate: "auto",
            // Ensure the center of the image sits on the path
            offsetAnchor: "50% 50%",
          }}
          initial={{ offsetDistance: "0%" }}
          animate={{ offsetDistance: "100%" }}
          transition={{ duration: 6, repeat: Infinity, ease: "anticipate" }}
        ></motion.div> */}
        {children ? children : "Button"}
        <motion.div
          initial={{ bottom: "-100%", left: "-100%" }}
          animate={{ bottom: "100%", left: "100%" }}
          transition={{ duration: 1.5, repeat: Infinity, repeatDelay: 6 }}
          className={`absolute h-[120%] w-[120%] rotate-45`}
          style={{
            background:
              "linear-gradient(to bottom, rgba(229, 172, 142, 0), rgba(255,255,255,0.5) 50%, rgba(229, 172, 142, 0))",
            // bottom: "-100%",
            // left: "-100%",
          }}
        ></motion.div>
      </motion.button>
    </>
  );
};
