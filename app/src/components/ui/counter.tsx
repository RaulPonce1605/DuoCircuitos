import Ionicons from "@expo/vector-icons/Ionicons";
import type { ComponentProps } from "react";
import { View } from "react-native";

import { AppText } from "@/components/ui/app-text";
import { useTheme } from "@/hooks/use-theme";
import type { ColorTokens } from "@/theme";

type Props = {
  icon: ComponentProps<typeof Ionicons>["name"];
  value: number;
  color: keyof ColorTokens;
  /** Frase completa para lectores de pantalla, ya traducida ("Racha de 3 días"). */
  accessibilityLabel: string;
  testID?: string;
};

/** Ícono + número: racha, EXP, energía... */
export function Counter({ icon, value, color, accessibilityLabel, testID }: Props) {
  const theme = useTheme();
  return (
    <View
      testID={testID}
      accessible
      accessibilityRole="text"
      accessibilityLabel={accessibilityLabel}
      style={{ flexDirection: "row", alignItems: "center", gap: theme.spacing.xs }}
    >
      <Ionicons name={icon} size={theme.sizes.iconMd} color={theme.colors[color]} />
      <AppText variant="bodyStrong" color={color}>
        {String(value)}
      </AppText>
    </View>
  );
}
