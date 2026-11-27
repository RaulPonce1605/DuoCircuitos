import Ionicons from "@expo/vector-icons/Ionicons";
import { useTranslation } from "react-i18next";
import { ActivityIndicator, View } from "react-native";

import { achievementGoal, achievementTitle, levelColor } from "@/components/achievements/names";
import { AppText, Button, Card, ProgressBar, Screen } from "@/components/ui";
import { useAchievements } from "@/hooks/use-achievements";
import { useTheme } from "@/hooks/use-theme";
import { errorMessage } from "@/i18n/error-message";
import type { Achievement } from "@/services/rewards-service";

function AchievementCard({ achievement }: { achievement: Achievement }) {
  const { t } = useTranslation();
  const theme = useTheme();
  const name = achievementTitle(achievement.id);
  const total = achievement.thresholds.length;
  const goal = achievement.next_threshold;
  // Avance dentro del nivel actual: de su umbral anterior al siguiente.
  const previous = achievement.level > 0 ? achievement.thresholds[achievement.level - 1] : 0;
  const progress = goal === null ? 1 : (achievement.value - previous) / Math.max(goal - previous, 1);

  return (
    <Card testID={`achievement-${achievement.id}`} style={{ gap: theme.spacing.sm }}>
      <View style={{ flexDirection: "row", alignItems: "center", gap: theme.spacing.md }}>
        <Ionicons
          name={achievement.level > 0 ? "trophy" : "trophy-outline"}
          size={theme.sizes.iconLg}
          color={theme.colors[achievement.level > 0 ? levelColor(achievement.level) : "locked"]}
        />
        <View style={{ flex: 1, gap: theme.spacing.xxs }}>
          <AppText variant="subtitle">{name}</AppText>
          <AppText variant="caption" color="textMuted">
            {t("achievements.level", { level: achievement.level, total })}
          </AppText>
        </View>
      </View>
      {goal === null ? (
        <AppText color="success">{t("achievements.completed")}</AppText>
      ) : (
        <>
          <AppText>{achievementGoal(achievement.id, goal)}</AppText>
          <ProgressBar progress={progress} color="xp" accessibilityLabel={t("achievements.progressLabel", { name })} />
          <AppText variant="caption" color="textMuted" align="right">
            {t("achievements.progress", { value: achievement.value, goal })}
          </AppText>
        </>
      )}
    </Card>
  );
}

/** Pantalla de logros: cada uno con su nivel y cuánto falta para el siguiente. */
export function AchievementsView() {
  const { t } = useTranslation();
  const theme = useTheme();
  const query = useAchievements();

  return (
    <Screen scroll>
      <AppText color="textMuted">{t("achievements.subtitle")}</AppText>
      {query.isPending ? (
        <ActivityIndicator
          color={theme.colors.primary}
          accessibilityLabel={t("achievements.loading")}
          style={{ marginTop: theme.spacing.xl }}
        />
      ) : query.isError ? (
        <View style={{ gap: theme.spacing.md }}>
          <AppText color="error" accessibilityRole="alert">
            {errorMessage(query.error)}
          </AppText>
          <Button label={t("common.retry")} variant="secondary" onPress={() => void query.refetch()} />
        </View>
      ) : (
        query.data.achievements.map((achievement) => (
          <AchievementCard key={achievement.id} achievement={achievement} />
        ))
      )}
    </Screen>
  );
}
