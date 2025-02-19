import { Button } from "@/components/ui/button";
import { useWebsocketStore } from "@/stores/WebsocketStore";

function TriggerDisconnectButton() {
  const { setConnected } = useWebsocketStore();

  return (
    <Button variant={"default"} onClick={() => setConnected(false)}>
      Trigger disconnect
    </Button>
  );
}

export default TriggerDisconnectButton;
