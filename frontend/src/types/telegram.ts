export type TmaPlatform = "android" | "ios" | "macos" | "tdesktop" | "weba" | "web" | "unknown";

export type TGInitParams = {
  tgWebAppData: string;
  tgWebAppVersion: string;
  tgWebAppPlatform: TmaPlatform;
  tgWebAppBotInline: string;
  tgWebAppThemeParams: string;
};
