import React, { createContext, useState, useContext, ReactNode, useEffect } from "react";

interface ThemeContextType {
  usingTGTheme: boolean;
  textColor: string;
  destructiveTextColor: string;
  bgColor: string;
  secondaryBGColor: string;
  hintColor: string;
  buttonColor: string;
  buttonTextColor: string;
  sectionSeparatorColor: string;
  linkColor: string;
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

interface ThemeProviderProps {
  children: ReactNode;
}

export const ThemeProvider: React.FC<ThemeProviderProps> = ({ children }) => {
  const [usingTGTheme, setUsingTGTheme] = useState(false);
  const [textColor, setTextColor] = useState("#fff");
  const [destructiveTextColor, setDestructiveTextColor] = useState("red");
  const [bgColor, setBgColor] = useState("#334155");
  const [secondaryBGColor, setsecondaryBGColor] = useState("#334155");
  const [hintColor, setHintColor] = useState("#fff");
  const [buttonColor, setButtonColor] = useState("");
  const [buttonTextColor, setButtonTextColor] = useState("#fff");
  const [sectionSeparatorColor, setSectionSeparatorColor] = useState("#fff");
  const [linkColor, setLinkColor] = useState("#fff");

  // const toggleTheme = () => {
  //   setTheme((prevTheme) => (prevTheme === 'light' ? 'dark' : 'light'));
  // };

  useEffect(() => {
    // @ts-ignore
    const theme = window.Telegram.WebApp.themeParams;
    if (theme) {
      setUsingTGTheme(true);
      setTextColor(theme.text_color);
      setDestructiveTextColor(theme.destructive_text_color);
      setBgColor(theme.bg_color);
      setsecondaryBGColor(theme.secondary_bg_color);
      setHintColor(theme.hint_color);
      setButtonColor(theme.button_color);
      setButtonTextColor(theme.button_text_color);
      setSectionSeparatorColor(theme.section_separator_color || theme.hint_color);
      setLinkColor(theme.link_color);

      document
        .querySelector("body")!
        .style.setProperty("background-color", theme.secondary_bg_color);
      // document.documentElement.style.setProperty(
      //   "--bg-color",
      //   theme.bg_color || "rgb(18, 17, 19)",
      // );
    } else {
      setUsingTGTheme(false);
    }
  }, []);

  const value: ThemeContextType = {
    usingTGTheme,
    textColor,
    destructiveTextColor,
    bgColor,
    secondaryBGColor,
    hintColor,
    buttonColor,
    buttonTextColor,
    sectionSeparatorColor,
    linkColor,
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
