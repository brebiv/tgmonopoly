import { useAuth } from "@/hooks";
import axios from "axios";
function Forbidden() {
  const { isError: isMeError, error } = useAuth();

  let errorMessage = "An error occurred";

  if (isMeError) {
    if (axios.isAxiosError(error)) {
      if (error.response && error.response.status === 403) {
        errorMessage = "Failed to verify that your request is valid";
      } else {
        errorMessage = "An unexpected error occurred";
      }
    } else {
      errorMessage = "An unexpected error occurred";
    }
  }

  return (
    <div
      className="flex min-h-screen w-full items-center justify-center"
      style={{
        backgroundColor:
          // @ts-ignore
          window.Telegram.WebApp.themeParams.bg_color || "#334155",
        // @ts-ignore
        color: window.Telegram.WebApp.themeParams.text_color || "white",
      }}
    >
      {errorMessage}
    </div>
  );
}

export default Forbidden;
