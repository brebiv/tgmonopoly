function ThemedDiv({ className, children }: { className?: string; children: React.ReactNode }) {
  return (
    <div
      className={className}
      style={{
        // @ts-ignore
        backgroundColor: window.Telegram.WebApp.themeParams.bg_color || "#334155",
        // @ts-ignore
        color: window.Telegram.WebApp.themeParams.text_color || "white",
      }}
    >
      {children}
    </div>
  );
}

export default ThemedDiv;
