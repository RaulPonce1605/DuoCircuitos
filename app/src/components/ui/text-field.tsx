import { useState } from "react";
import { TextInput, type TextInputProps, View } from "react-native";

import { AppText } from "@/components/ui/app-text";
import { useTheme } from "@/hooks/use-theme";

type Props = Omit<TextInputProps, "style" | "placeholderTextColor"> & {
  label: string;
  error?: string | null;
  hint?: string;
};

export function TextField({ label, error, hint, onFocus, onBlur, ...props }: Props) {
  const theme = useTheme();
  const [focused, setFocused] = useState(false);
  const borderColor = error
    ? theme.colors.error
    : focused
      ? theme.colors.primary
      : theme.colors.border;

  return (
    <View style={{ gap: theme.spacing.xs }}>
      <AppText variant="bodyStrong">{label}</AppText>
      <TextInput
        {...props}
        accessibilityLabel={label}
        accessibilityHint={error ?? hint}
        onFocus={(event) => {
          setFocused(true);
          onFocus?.(event);
        }}
        onBlur={(event) => {
          setFocused(false);
          onBlur?.(event);
        }}
        placeholderTextColor={theme.colors.textMuted}
        style={[
          theme.typography.body,
          {
            minHeight: theme.sizes.touchTarget,
            paddingHorizontal: theme.spacing.md,
            borderRadius: theme.radii.md,
            borderWidth: theme.borders.thick,
            borderColor,
            backgroundColor: theme.colors.surface,
            color: theme.colors.text,
          },
        ]}
      />
      {error ? (
        <AppText variant="caption" color="error" accessibilityLiveRegion="polite">
          {error}
        </AppText>
      ) : hint ? (
        <AppText variant="caption" color="textMuted">
          {hint}
        </AppText>
      ) : null}
    </View>
  );
}
