import { ActivityIndicator, Pressable, StyleSheet, View } from "react-native";

import { AppText } from "@/components/ui/app-text";
import { useTheme } from "@/hooks/use-theme";
import type { ColorTokens } from "@/theme";

export type ButtonVariant = "primary" | "secondary" | "success" | "danger";

type Props = {
  label: string;
  onPress: () => void;
  variant?: ButtonVariant;
  disabled?: boolean;
  loading?: boolean;
  fullWidth?: boolean;
  accessibilityHint?: string;
  testID?: string;
};

const PALETTE: Record<
  ButtonVariant,
  { background: keyof ColorTokens; pressed: keyof ColorTokens; text: keyof ColorTokens }
> = {
  primary: { background: "primary", pressed: "primaryPressed", text: "textOnPrimary" },
  secondary: { background: "surface", pressed: "surfaceMuted", text: "primary" },
  success: { background: "success", pressed: "success", text: "textOnPrimary" },
  danger: { background: "error", pressed: "error", text: "textOnPrimary" },
};

export function Button({
  label,
  onPress,
  variant = "primary",
  disabled = false,
  loading = false,
  fullWidth = true,
  accessibilityHint,
  testID,
}: Props) {
  const theme = useTheme();
  const colors = PALETTE[variant];
  const inactive = disabled || loading;

  return (
    <Pressable
      testID={testID}
      onPress={onPress}
      disabled={inactive}
      accessibilityRole="button"
      accessibilityLabel={label}
      accessibilityHint={accessibilityHint}
      accessibilityState={{ disabled: inactive, busy: loading }}
      style={({ pressed }) => [
        styles.base,
        {
          minHeight: theme.sizes.touchTarget,
          borderRadius: theme.radii.md,
          paddingHorizontal: theme.spacing.lg,
          backgroundColor: theme.colors[pressed ? colors.pressed : colors.background],
          borderColor: variant === "secondary" ? theme.colors.border : "transparent",
          borderWidth: theme.borders.thick,
          opacity: disabled ? 0.5 : 1,
          alignSelf: fullWidth ? "stretch" : "center",
        },
      ]}
    >
      <View style={styles.content}>
        {loading ? (
          <ActivityIndicator color={theme.colors[colors.text]} />
        ) : (
          <AppText variant="button" color={colors.text}>
            {label.toUpperCase()}
          </AppText>
        )}
      </View>
    </Pressable>
  );
}

const styles = StyleSheet.create({
  base: { justifyContent: "center" },
  content: { alignItems: "center", justifyContent: "center" },
});
