// Paleta PROVISIONAL propia (cobre y verde azulado, como una placa de circuito).
// Los tokens definitivos son una tarea de la fase 1; aquí solo se cambian los valores.

export type ColorTokens = {
  background: string;
  surface: string;
  surfaceMuted: string;
  border: string;
  text: string;
  textMuted: string;
  textOnPrimary: string;
  primary: string;
  primaryPressed: string;
  accent: string;
  success: string;
  error: string;
  warning: string;
};

export const lightColors: ColorTokens = {
  background: "#F7F5F2",
  surface: "#FFFFFF",
  surfaceMuted: "#ECE8E3",
  border: "#D6D0C8",
  text: "#1D2327",
  textMuted: "#5C666D",
  textOnPrimary: "#FFFFFF",
  primary: "#0E7C86",
  primaryPressed: "#0A5F67",
  accent: "#C8692B",
  success: "#2B8A3E",
  error: "#C92A2A",
  warning: "#E0A100",
};

export const darkColors: ColorTokens = {
  background: "#12171A",
  surface: "#1B2227",
  surfaceMuted: "#252E34",
  border: "#34404A",
  text: "#ECEFF1",
  textMuted: "#A3ADB4",
  textOnPrimary: "#071416",
  primary: "#3CC1CC",
  primaryPressed: "#2AA3AD",
  accent: "#F0934F",
  success: "#55C26B",
  error: "#F06363",
  warning: "#F5C542",
};
