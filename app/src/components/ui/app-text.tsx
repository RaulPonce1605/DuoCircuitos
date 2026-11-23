import { Text, type TextProps } from "react-native";

import { useTheme } from "@/hooks/use-theme";
import type { ColorTokens, Theme } from "@/theme";

export type AppTextProps = TextProps & {
  variant?: keyof Theme["typography"];
  color?: keyof ColorTokens;
  align?: "left" | "center" | "right";
};

/** Texto con la tipografía y los colores del tema. El contenido siempre viene de i18n. */
export function AppText({
  variant = "body",
  color = "text",
  align,
  style,
  ...props
}: AppTextProps) {
  const theme = useTheme();
  return (
    <Text
      {...props}
      style={[
        theme.typography[variant],
        { color: theme.colors[color] },
        align ? { textAlign: align } : null,
        style,
      ]}
    />
  );
}
