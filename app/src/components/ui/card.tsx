import type { ReactNode } from "react";
import { Pressable, View, type ViewStyle } from "react-native";

import { useTheme } from "@/hooks/use-theme";
import type { ColorTokens } from "@/theme";

type Props = {
  children: ReactNode;
  /** Si se pasa, la tarjeta es un botón. */
  onPress?: () => void;
  accessibilityLabel?: string;
  tone?: keyof ColorTokens;
  borderTone?: keyof ColorTokens;
  style?: ViewStyle;
  testID?: string;
};

export function Card({
  children,
  onPress,
  accessibilityLabel,
  tone = "surface",
  borderTone = "border",
  style,
  testID,
}: Props) {
  const theme = useTheme();
  const base: ViewStyle = {
    backgroundColor: theme.colors[tone],
    borderColor: theme.colors[borderTone],
    borderWidth: theme.borders.thick,
    borderRadius: theme.radii.lg,
    padding: theme.spacing.md,
  };

  if (!onPress) {
    return (
      <View testID={testID} style={[base, style]}>
        {children}
      </View>
    );
  }
  return (
    <Pressable
      testID={testID}
      onPress={onPress}
      accessibilityRole="button"
      accessibilityLabel={accessibilityLabel}
      style={({ pressed }) => [base, pressed ? { opacity: 0.85 } : null, style]}
    >
      {children}
    </Pressable>
  );
}
