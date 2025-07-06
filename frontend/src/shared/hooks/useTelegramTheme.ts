import { useEffect } from "react";

export function useTelegramColorScheme() {
  useEffect(() => {
    const tg = Telegram.WebApp;
    if (!tg) return;

    const apply = () => {
      document.documentElement.classList.remove("dark");
      document.documentElement.classList.remove("light");
      document.documentElement.classList.add(tg.colorScheme);
    };

    apply();
    tg.onEvent("themeChanged", apply);
    return () => tg.offEvent("themeChanged", apply);
  }, []);
}
