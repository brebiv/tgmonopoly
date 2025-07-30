import { Card } from "@/shared/ui/Card";
import { cn } from "@/shared/utils";

import checkmark from "@/assets/checkmark.png";
import coins from "@/assets/coins.png";
import { FancyJuicyButton } from "./FancyJuicyButton";

interface DailyRewardProps {}

export const DailyReward = ({}: DailyRewardProps) => {
  return (
    <Card
      className="bg-accent-text"
      style={{
        background:
          "linear-gradient(0deg,var(--color-secondary-background) 00%, var(--color-accent-text) 100%",
      }}
    >
      <div className="flex flex-col items-center gap-4">
        <h1 className="text-button-text text-lin uppercase">Daily reward</h1>
        <div className="grid h-20 w-full grid-cols-5 gap-2">
          {Array.from({ length: 5 }).map((_, i) => (
            <div
              className={cn("bg-button border-button relative flex w-full flex-col rounded-md border-1", {
                "outline-button-text border-0 outline-2": i == 3,
              })}
            >
              <div
                className="z-10 flex h-full w-full flex-col rounded-md"
                style={{
                  background: "linear-gradient(180deg,var(--color-accent-text) 0%, var(--color-button) 100%",
                }}
              >
                <div
                  className={cn("flex h-4 w-full items-center rounded-t-md", {
                    "bg-secondary-background": i == 3,
                  })}
                  style={{
                    background:
                      i == 3
                        ? ""
                        : "linear-gradient(180deg,var(--color-accent-text) 0%, var(--color-button) 100%",
                  }}
                >
                  <p
                    className={cn("text-button-text w-full text-center text-xs", {
                      "text-current": i == 3,
                    })}
                  >
                    Day {i + 1}
                  </p>
                </div>
                <div className="h-full w-full">
                  {i < 3 && <img src={checkmark} />}
                  {i > 2 && <img src={coins} />}
                </div>
                <div
                  className="bg-secondary-background mt-auto flex h-4 w-full items-center rounded-b-md"
                  style={{
                    background:
                      i != 3
                        ? ""
                        : "linear-gradient(180deg,var(--color-accent-text) 0%, var(--color-button) 100%",
                  }}
                >
                  <p
                    className={cn("w-full text-center text-xs", {
                      "text-button-text": i == 3,
                    })}
                  >
                    +{(i + 1) * 100}
                  </p>
                </div>
              </div>
            </div>
          ))}
        </div>
        <div className="w-full">
          <FancyJuicyButton className="w-full" fireConfetti>
            Claim
          </FancyJuicyButton>
        </div>
      </div>
    </Card>
  );
};
