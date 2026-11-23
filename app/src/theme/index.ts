import type { TextStyle } from "react-native";

import { type ColorTokens, darkColors, lightColors } from "./colors";

/** Familias de fuente. Se cargan en `src/components/app-providers.tsx`. */
export const fonts = {
  heading: "SpaceGrotesk_700Bold",
  headingMedium: "SpaceGrotesk_600SemiBold",
  // El cuerpo usa la fuente del sistema: es la más legible en cada plataforma.
  body: undefined,
} as const;

/** Escala de 4 pt. */
export const spacing = {
  xxs: 2,
  xs: 4,
  sm: 8,
  md: 16,
  lg: 24,
  xl: 32,
  xxl: 48,
} as const;

export const radii = {
  sm: 8,
  md: 14,
  lg: 20,
  pill: 999,
} as const;

export const borders = {
  thin: 1,
  thick: 2,
} as const;

export const sizes = {
  /** Área táctil mínima (accesibilidad). */
  touchTarget: 48,
  iconSm: 18,
  iconMd: 24,
  iconLg: 32,
  progressBar: 14,
  /** Ancho máximo del contenido en pantallas grandes (web). */
  contentMaxWidth: 560,
} as const;

type Typography = Record<
  "display" | "title" | "subtitle" | "body" | "bodyStrong" | "caption" | "button",
  TextStyle
>;

export const typography: Typography = {
  display: { fontFamily: fonts.heading, fontSize: 34, lineHeight: 40 },
  title: { fontFamily: fonts.heading, fontSize: 26, lineHeight: 32 },
  subtitle: { fontFamily: fonts.headingMedium, fontSize: 19, lineHeight: 25 },
  body: { fontSize: 16, lineHeight: 23 },
  bodyStrong: { fontSize: 16, lineHeight: 23, fontWeight: "700" },
  caption: { fontSize: 13, lineHeight: 18 },
  button: { fontFamily: fonts.heading, fontSize: 16, lineHeight: 20, letterSpacing: 0.4 },
};

export type Theme = {
  dark: boolean;
  colors: ColorTokens;
  spacing: typeof spacing;
  radii: typeof radii;
  borders: typeof borders;
  sizes: typeof sizes;
  typography: Typography;
};

const shared = { spacing, radii, borders, sizes, typography };

export const lightTheme: Theme = { dark: false, colors: lightColors, ...shared };
export const darkTheme: Theme = { dark: true, colors: darkColors, ...shared };

export type { ColorTokens };
