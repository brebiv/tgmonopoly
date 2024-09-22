function LoadingScreen() {
  return (
    <div
      className="flex min-h-screen w-full flex-col items-center justify-center gap-4"
      style={{
        // @ts-ignore
        backgroundColor: window.Telegram.WebApp.themeParams.bg_color,
        // @ts-ignore
        color: window.Telegram.WebApp.themeParams.text_color,
      }}
    >
      <h1>Loading...</h1>
    </div>
  );
}

export default LoadingScreen;
