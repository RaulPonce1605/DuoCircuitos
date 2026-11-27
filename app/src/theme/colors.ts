// Paleta propia de Circuitos: verde azulado de placa de circuito + cobre de las pistas.
// Documentada en docs/diseno/tokens.md. Para cambiar la identidad se editan SOLO estos valores.

export type ColorTokens = {
  // Superficies
  background: string;
  surface: string;
  surfaceMuted: string;
  border: string;
  // Texto
  text: string;
  textMuted: string;
  textOnPrimary: string;
  // Marca
  primary: string;
  primaryPressed: string;
  primarySoft: string;
  accent: string;
  accentSoft: string;
  // Estados de una respuesta
  success: string;
  successSoft: string;
  error: string;
  errorSoft: string;
  warning: string;
  // Gamificación
  xp: string;
  streak: string;
  energy: string;
  coins: string;
  locked: string;
};

export const lightColors: ColorTokens = {
  background: "#F6F4F0",
  surface: "#FFFFFF",
  surfaceMuted: "#ECE8E2",
  border: "#D7D0C6",
  text: "#1B2327",
  textMuted: "#56626A",
  textOnPrimary: "#FFFFFF",
  primary: "#0B6E77",
  primaryPressed: "#08555C",
  primarySoft: "#D5ECEE",
  accent: "#B85C22",
  accentSoft: "#F5E3D6",
  success: "#24793A",
  successSoft: "#DDF0E1",
  error: "#B3261E",
  errorSoft: "#F9DEDC",
  warning: "#9A6B00",
  xp: "#8A5A00",
  streak: "#C2491D",
  energy: "#2F5FB3",
  coins: "#7A5C00",
  locked: "#A39C92",
};

export const darkColors: ColorTokens = {
  background: "#101517",
  surface: "#192125",
  surfaceMuted: "#232D32",
  border: "#33414A",
  text: "#ECEFF1",
  textMuted: "#A6B0B6",
  textOnPrimary: "#04191B",
  primary: "#45C3CD",
  primaryPressed: "#2EA6B0",
  primarySoft: "#123A3E",
  accent: "#F0965A",
  accentSoft: "#43281A",
  success: "#5CC97A",
  successSoft: "#173823",
  error: "#F2827A",
  errorSoft: "#47201D",
  warning: "#F2C14E",
  xp: "#F2C14E",
  streak: "#FF8A57",
  energy: "#82AEF5",
  coins: "#E8C547",
  locked: "#5E676D",
};
