import { type ColorTokens, darkColors, lightColors } from "./colors";

export const spacing = {
  xs: 4,
  sm: 8,
  md: 16,
  lg: 24,
  xl: 32,
  xxl: 48,
} as const;

export const radii = {
  sm: 6,
  md: 12,
  lg: 20,
  pill: 999,
} as const;

export const typography = {
  // Fuentes del sistema hasta definir una tipografía propia.
  title: { fontSize: 28, lineHeight: 34, fontWeight: "700" },
  subtitle: { fontSize: 20, lineHeight: 26, fontWeight: "600" },
  body: { fontSize: 16, lineHeight: 22, fontWeight: "400" },
  caption: { fontSize: 13, lineHeight: 18, fontWeight: "400" },
  button: { fontSize: 16, lineHeight: 20, fontWeight: "700" },
} as const;

export type Theme = {
  colors: ColorTokens;
  spacing: typeof spacing;
  radii: typeof radii;
  typography: typeof typography;
};

export const lightTheme: Theme = { colors: lightColors, spacing, radii, typography };
export const darkTheme: Theme = { colors: darkColors, spacing, radii, typography };

export type { ColorTokens };
