import React, { createContext, useState, useContext, ReactNode, useEffect } from "react";

interface ThemeContextType {
  usingTGTheme: boolean;
  textColor: string;
  destructiveColor: string;
  bgColor: string;
  secondaryBGColor: string;
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

interface ThemeProviderProps {
  children: ReactNode;
}

export const ThemeProvider: React.FC<ThemeProviderProps> = ({ children }) => {
  const [usingTGTheme, setUsingTGTheme] = useState(false);
  const [textColor, setTextColor] = useState("#fff");
  const [destructiveColor, setDestructiveColor] = useState("red");
  const [bgColor, setBgColor] = useState("#334155");
  const [secondaryBGColor, setsecondaryBGColor] = useState("#334155");

  // const toggleTheme = () => {
  //   setTheme((prevTheme) => (prevTheme === 'light' ? 'dark' : 'light'));
  // };

  useEffect(() => {
    // @ts-ignore
    const theme = window.Telegram.WebApp.themeParams;
    if (theme) {
      setUsingTGTheme(true);
      setTextColor(theme.text_color);
      setDestructiveColor(theme.destructive_text_color);
      setBgColor(theme.bg_color);
      setsecondaryBGColor(theme.secondary_bg_color);
    } else {
      setUsingTGTheme(false);
    }
  }, []);

  const value: ThemeContextType = {
    usingTGTheme,
    textColor,
    destructiveColor,
    bgColor,
    secondaryBGColor,
  };

  return <ThemeContext.Provider value={value}>{children}</ThemeContext.Provider>;
};

export const useTheme = (): ThemeContextType => {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error("useTheme must be used within a ThemeProvider");
  }
  return context;
};
