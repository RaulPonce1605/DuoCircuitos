import { useTranslation } from "react-i18next";
import { StyleSheet, Text, View } from "react-native";

import { useTheme } from "@/hooks/use-theme";

export function Welcome() {
  const { t } = useTranslation();
  const theme = useTheme();

  return (
    <View
      style={[
        styles.container,
        { backgroundColor: theme.colors.background, padding: theme.spacing.lg },
      ]}
    >
      <Text style={[theme.typography.title, { color: theme.colors.primary }]}>
        {t("app.name")}
      </Text>
      <Text
        style={[
          theme.typography.body,
          { color: theme.colors.textMuted, marginTop: theme.spacing.sm },
        ]}
      >
        {t("app.tagline")}
      </Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, alignItems: "center", justifyContent: "center" },
});
