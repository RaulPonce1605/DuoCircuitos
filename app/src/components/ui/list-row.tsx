import Ionicons from "@expo/vector-icons/Ionicons";
import type { ComponentProps, ReactNode } from "react";
import { Pressable, View } from "react-native";

import { AppText } from "@/components/ui/app-text";
import { useTheme } from "@/hooks/use-theme";
import type { ColorTokens } from "@/theme";

type Props = {
  icon: ComponentProps<typeof Ionicons>["name"];
  label: string;
  /** Texto chico debajo de la etiqueta. */
  detail?: string;
  iconColor?: keyof ColorTokens;
  /** Si se pasa, la fila es un botón con flecha. */
  onPress?: () => void;
  /** Algo a la derecha (un interruptor, un valor). */
  trailing?: ReactNode;
  testID?: string;
};

/** Fila de menú o de ajustes: ícono, texto y, a la derecha, una flecha o un control. */
export function ListRow({ icon, label, detail, iconColor = "primary", onPress, trailing, testID }: Props) {
  const theme = useTheme();
  const content = (
    <>
      <Ionicons name={icon} size={theme.sizes.iconMd} color={theme.colors[iconColor]} />
      <View style={{ flex: 1, gap: theme.spacing.xxs }}>
        <AppText variant="bodyStrong">{label}</AppText>
        {detail ? (
          <AppText variant="caption" color="textMuted">
            {detail}
          </AppText>
        ) : null}
      </View>
      {trailing ??
        (onPress ? <Ionicons name="chevron-forward" size={theme.sizes.iconSm} color={theme.colors.textMuted} /> : null)}
    </>
  );
  const style = {
    flexDirection: "row" as const,
    alignItems: "center" as const,
    gap: theme.spacing.md,
    minHeight: theme.sizes.touchTarget,
    paddingVertical: theme.spacing.sm,
  };
  if (!onPress) {
    return (
      <View testID={testID} style={style}>
        {content}
      </View>
    );
  }
  return (
    <Pressable
      testID={testID}
      onPress={onPress}
      accessibilityRole="button"
      accessibilityLabel={detail ? `${label}, ${detail}` : label}
      style={({ pressed }) => [style, { opacity: pressed ? 0.7 : 1 }]}
    >
      {content}
    </Pressable>
  );
}
