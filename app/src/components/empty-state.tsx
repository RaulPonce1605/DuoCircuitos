import Ionicons from "@expo/vector-icons/Ionicons";
import type { ComponentProps } from "react";
import { View } from "react-native";

import { AppText } from "@/components/ui";
import { useTheme } from "@/hooks/use-theme";

type Props = {
  icon: ComponentProps<typeof Ionicons>["name"];
  title: string;
  message: string;
};

export function EmptyState({ icon, title, message }: Props) {
  const theme = useTheme();
  return (
    <View style={{ flex: 1, alignItems: "center", justifyContent: "center", gap: theme.spacing.sm }}>
      <Ionicons name={icon} size={theme.sizes.iconLg * 2} color={theme.colors.primary} />
      <AppText variant="title" align="center" accessibilityRole="header">
        {title}
      </AppText>
      <AppText color="textMuted" align="center">
        {message}
      </AppText>
    </View>
  );
}
