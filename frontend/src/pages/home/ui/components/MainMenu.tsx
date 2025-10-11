// @ts-nocheck
import { Button } from "@/shared/ui/Button";
import { Shining } from "@/shared/ui/Shining";
import { LineChart, Line, ResponsiveContainer, XAxis, YAxis, BarChart, AreaChart, Area } from "recharts";
import { ChartNoAxesCombinedIcon, GoalIcon } from "lucide-react";
import { TopBaner } from "./TopBanner";
import { Card } from "@/shared/ui/Card";

const mockMissions = [
  { id: "mission-1", title: "Win 3 games", progress: 0.66, reward: 100 },
  { id: "mission-2", title: "Play with a friend", progress: 0.5, reward: 50 },
  { id: "mission-3", title: "Join a tournament", progress: 0, reward: 200 },
];
const data = [
  { total: 1610.73512929 },
  { total: 1611.39780849 },
  { total: 1611.46790181 },
  { total: 1610.09380156 },
  { total: 1609.27040911 },
  { total: 1610.09137125 },
  { total: 1611.05387252 },
  { total: 1611.98722364 },
  { total: 1610.01581063 },
  { total: 1611.79708787 },
  { total: 1612.17309647 },
  { total: 1613.48657918 },
  { total: 1613.70250613 },
  { total: 1613.35201633 },
  { total: 1613.65636562 },
  { total: 1612.15116951 },
  { total: 1610.02847246 },
  { total: 1611.15664407 },
  { total: 1611.48125994 },
  { total: 1611.39478574 },
  { total: 1611.95409196 },
  { total: 1611.54287081 },
  { total: 1611.87479161 },
  { total: 1613.16065028 },
  { total: 1613.46485707 },
  { total: 1612.36203008 },
  { total: 1612.51440341 },
  { total: 1612.81035805 },
  { total: 1613.26233223 },
  { total: 1611.37191131 },
];

export const MainMenu = () => {
  return (
    <div className="flex h-full w-full grow flex-col gap-6 pb-4">
      <TopBaner />
      <div className="grid h-full w-full grid-cols-2 grid-rows-[auto_1fr] gap-4">
        <div className="col-span-2 grid grid-cols-subgrid">
          <Card className="gap-3 px-2">
            <p className="flex gap-2 text-xl font-medium">
              <GoalIcon />
              Missions
            </p>
            <div className="flex flex-col gap-1">
              {mockMissions.map((m) => (
                // <div key={m.id} className="rounded-xl bg-slate-900/90 p-2">
                <div key={m.id} className="bg-secondary-background/90 rounded-xl p-2">
                  <div className="flex items-center justify-between text-xs">
                    <span>{m.title}</span>
                    <span className="text-accent-text opacity-70">+{m.reward}</span>
                  </div>
                  <div className="mt-1 h-1.5 w-full overflow-hidden rounded-full bg-white/10">
                    <div
                      className="bg-accent-text h-full"
                      style={{ width: `${Math.min(100, Math.round(m.progress * 100))}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </Card>
          <Card className="gap-3 px-2">
            <p className="flex gap-2 text-xl font-medium">
              <ChartNoAxesCombinedIcon />
              Net Worth
            </p>
            <div className="h-full w-full">
              <ResponsiveContainer>
                <AreaChart data={data} className="pointer-events-none">
                  <defs>
                    <linearGradient id="totalGradient" x1="0" y1="0" x2="0" y2="1">
                      <stop
                        offset="0%"
                        stopColor={Telegram.WebApp.themeParams.accent_text_color}
                        stopOpacity={0.35}
                      />
                      <stop
                        offset="100%"
                        stopColor={Telegram.WebApp.themeParams.accent_text_color}
                        stopOpacity={0}
                      />
                    </linearGradient>
                  </defs>
                  <YAxis domain={[(min) => min * 0.995, (max) => max * 1.005]} hide />
                  <Area
                    type={"natural"}
                    dataKey={"total"}
                    dot={false}
                    strokeWidth={2}
                    stroke={Telegram.WebApp.themeParams.accent_text_color}
                    fill="url(#totalGradient)"
                    fillOpacity={1}
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
};
// export const MainMenu = () => {
//   return (
//     <div className="col-span-2 row-span-2 flex h-full w-full grow flex-col gap-6 bg-red-500 pb-4">
//       {/* System status header */}
//       {/* <div className="flex">
//         <div className="flex gap-2">
//           <div className="flex gap-1">
//             <UsersRoundIcon /> 7k
//           </div>
//           <div className="flex gap-1">
//             <Gamepad2Icon /> 532
//           </div>
//         </div>
//       </div> */}

//       {/* Buttons */}
//       {/* <div className="mt-auto flex w-full flex-col items-center gap-4"> */}
//       <div className="relative flex gap-8">
//         <div className="relative flex grow-0 items-center justify-start">
//           <Button className="flex gap-1 rounded-xl p-4 text-xl font-extrabold">
//             <SettingsIcon />
//           </Button>
//         </div>
//         <div className="relative bottom-4 flex shrink-0 grow-3">
//           <Button className="flex w-full gap-1 rounded-xl p-4 text-xl font-extrabold">Play</Button>
//           <div className="pointer-events-none absolute h-full w-full rounded-xl">
//             <Shining />
//           </div>
//         </div>
//         <div className="relative flex items-center justify-end">
//           <Button className="flex gap-1 rounded-xl p-4 text-xl font-extrabold">
//             <PlusIcon />
//           </Button>
//         </div>
//         {/* <Button className="flex w-1/2 gap-1 p-4 font-medium">
//           <Gamepad2Icon />
//           Create lobby
//         </Button> */}

//         {/* <div className="w-fulll mt-auto flex items-center justify-center">
//           <Button>Quick Join</Button>
//         </div> */}
//       </div>
//     </div>
//   );
// };
