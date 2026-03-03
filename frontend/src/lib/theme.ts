export type Theme = "light" | "dark";

const THEME_KEY = "memory-theme";
const DEFAULT_THEME: Theme = "dark";

const normalizeTheme = (value: string | null): Theme => {
  return value === "light" || value === "dark" ? value : DEFAULT_THEME;
};

export const getStoredTheme = (): Theme => {
  if (typeof window === "undefined") {
    return DEFAULT_THEME;
  }

  return normalizeTheme(window.localStorage.getItem(THEME_KEY));
};

export const applyTheme = (theme: Theme): void => {
  if (typeof document === "undefined") {
    return;
  }

  document.documentElement.classList.toggle("dark", theme === "dark");
};

export const setStoredTheme = (theme: Theme): void => {
  if (typeof window !== "undefined") {
    window.localStorage.setItem(THEME_KEY, theme);
  }

  applyTheme(theme);
};

export const initializeTheme = (): Theme => {
  const theme = getStoredTheme();
  applyTheme(theme);
  return theme;
};
