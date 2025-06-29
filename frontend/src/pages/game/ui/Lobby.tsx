import { useReactQuerySubscription } from "@/shared/hooks/useReactQuerySubscription";
import { Button } from "@/shared/ui/Button";

export const Lobby = () => {
  const { send } = useReactQuerySubscription(
    "87462c62-2c01-499d-bbc9-26eea8b38c78"
  );
  return (
    <div>
      <Button
        onClick={() => {
          send("hello");
        }}
      >
        Lobby
      </Button>
    </div>
  );
};
