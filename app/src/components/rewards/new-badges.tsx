import Ionicons from "@expo/vector-icons/Ionicons";
import { useTranslation } from "react-i18next";
import { View } from "react-native";

import { achievementGoal, badgeName, levelColor } from "@/components/achievements/names";
import { AppText, Card } from "@/components/ui";
import { useTheme } from "@/hooks/use-theme";
import type { Badge } from "@/services/rewards-service";

/** Celebra las medallas recién ganadas (resumen de lección, cofre). */
export function NewBadges({ badges }: { badges: Badge[] }) {
  const { t } = useTranslation();
  const theme = useTheme();
  if (badges.length === 0) {
    return null;
  }
  return (
    <Card testID="new-badges" borderTone="accent" style={{ gap: theme.spacing.sm }}>
      <AppText variant="subtitle" accessibilityRole="header">
        {t("badges.new", { count: badges.length })}
      </AppText>
      {badges.map((badge) => (
        <View
          key={`${badge.achievement_id}-${badge.level}`}
          style={{ flexDirection: "row", alignItems: "center", gap: theme.spacing.sm }}
        >
          <Ionicons name="medal" size={theme.sizes.iconLg} color={theme.colors[levelColor(badge.level)]} />
          <View style={{ flex: 1 }}>
            <AppText variant="bodyStrong">{badgeName(badge)}</AppText>
            <AppText variant="caption" color="textMuted">
              {achievementGoal(badge.achievement_id, badge.threshold)}
            </AppText>
          </View>
        </View>
      ))}
    </Card>
  );
}
