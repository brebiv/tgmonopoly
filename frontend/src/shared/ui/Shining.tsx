import { motion } from "motion/react";

interface ShiningProps {
  duration?: number;
  repeat?: number;
  repeatDelay?: number;
  delay?: number;
}

export const Shining = ({
  duration = 1.5,
  repeat = Infinity,
  repeatDelay = 6,
  delay = 0.5,
}: ShiningProps) => {
  return (
    <div className="relative h-full w-full overflow-hidden rounded-[inherit]">
      <motion.div
        initial={{ bottom: "-100%", left: "-100%" }}
        animate={{ bottom: "100%", left: "100%" }}
        transition={{ duration: duration, repeat: repeat, repeatDelay: repeatDelay, delay: delay }}
        className={`absolute h-[120%] w-[120%] rotate-45`}
        style={{
          background:
            "linear-gradient(to bottom, rgba(229, 172, 142, 0), rgba(255,255,255,0.5) 50%, rgba(229, 172, 142, 0))",
        }}
      />
    </div>
  );
};
