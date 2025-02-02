import { Avatar, AvatarFallback } from "../ui/avatar";
import { Card, CardContent } from "../ui/card";
import { useTheme } from "@/stores/ThemeContext";

function PlayerCardSkeleton() {
  const { hintColor } = useTheme();

  return (
    <Card className="relative">
      <CardContent className="flex gap-3 p-2">
        <div className="relative">
          <div
            className="absolute aspect-square rounded-full"
            style={{
              width: "calc(100% + 4px)",
              top: "-2px",
              left: "-2px",
              transition: "background 0.5s ease",
            }}
          ></div>
          <Avatar>
            <AvatarFallback
              className="border-2 border-dashed"
              style={{ backgroundColor: "transparent", borderColor: hintColor }}
            ></AvatarFallback>
          </Avatar>
        </div>
        <div className="h-full w-full">
          <p className="text-sm">------------</p>
          <p
            className="text-sm font-thin"
            style={{
              color: hintColor,
            }}
          >
            ------
          </p>
        </div>
      </CardContent>
    </Card>
  );
}

export default PlayerCardSkeleton;
