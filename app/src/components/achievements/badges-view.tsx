import Ionicons from "@expo/vector-icons/Ionicons";
import { useTranslation } from "react-i18next";
import { ActivityIndicator, View } from "react-native";

import { achievementGoal, badgeName, levelColor } from "@/components/achievements/names";
import { AppText, Button, Card, Screen } from "@/components/ui";
import { useAchievements } from "@/hooks/use-achievements";
import { useTheme } from "@/hooks/use-theme";
import { errorMessage } from "@/i18n/error-message";
import type { Achievements, Badge } from "@/services/rewards-service";

type Slot = { achievementId: string; level: number; threshold: number; earned: Badge | null };

/** Todas las medallas posibles (cada nivel de cada logro), ganadas o no. */
export function badgeSlots(data: Achievements): Slot[] {
  const earned = new Map(data.badges.map((badge) => [`${badge.achievement_id}:${badge.level}`, badge]));
  return data.achievements.flatMap((achievement) =>
    achievement.thresholds.map((threshold, index) => ({
      achievementId: achievement.id,
      level: index + 1,
      threshold,
      earned: earned.get(`${achievement.id}:${index + 1}`) ?? null,
    })),
  );
}

function BadgeTile({ slot }: { slot: Slot }) {
  const { t, i18n } = useTranslation();
  const theme = useTheme();
  const name = badgeName({ achievement_id: slot.achievementId, level: slot.level });
  const status = slot.earned
    ? t("badges.earnedOn", {
        date: new Date(slot.earned.earned_at).toLocaleDateString(i18n.language, { dateStyle: "medium" }),
      })
    : t("badges.locked");
  return (
    <Card
      testID={`badge-${slot.achievementId}-${slot.level}`}
      borderTone={slot.earned ? levelColor(slot.level) : "border"}
      style={{ flexBasis: 150, flexGrow: 1, alignItems: "center", gap: theme.spacing.xs }}
    >
      <View accessible accessibilityLabel={`${name}. ${status}`} style={{ alignItems: "center", gap: theme.spacing.xs }}>
        <Ionicons
          name={slot.earned ? "medal" : "lock-closed"}
          size={theme.sizes.iconLg * 1.5}
          color={theme.colors[slot.earned ? levelColor(slot.level) : "locked"]}
        />
        <AppText variant="bodyStrong" align="center" color={slot.earned ? "text" : "textMuted"}>
          {name}
        </AppText>
        <AppText variant="caption" color="textMuted" align="center">
          {achievementGoal(slot.achievementId, slot.threshold)}
        </AppText>
        <AppText variant="caption" color={slot.earned ? "success" : "textMuted"} align="center">
          {status}
        </AppText>
      </View>
    </Card>
  );
}

/** Pantalla de medallas: las ganadas primero y las que faltan bloqueadas. */
export function BadgesView() {
  const { t } = useTranslation();
  const theme = useTheme();
  const query = useAchievements();

  if (query.isPending || query.isError) {
    return (
      <Screen>
        {query.isPending ? (
          <ActivityIndicator
            color={theme.colors.primary}
            accessibilityLabel={t("badges.loading")}
            style={{ marginTop: theme.spacing.xl }}
          />
        ) : (
          <View style={{ gap: theme.spacing.md }}>
            <AppText color="error" accessibilityRole="alert">
              {errorMessage(query.error)}
            </AppText>
            <Button label={t("common.retry")} variant="secondary" onPress={() => void query.refetch()} />
          </View>
        )}
      </Screen>
    );
  }

  const slots = badgeSlots(query.data);
  const earned = slots.filter((slot) => slot.earned !== null);
  const ordered = [...earned, ...slots.filter((slot) => slot.earned === null)];
  return (
    <Screen scroll>
      <AppText color="textMuted">{t("badges.subtitle")}</AppText>
      <AppText variant="subtitle">{t("badges.earnedCount", { earned: earned.length, total: slots.length })}</AppText>
      <View style={{ flexDirection: "row", flexWrap: "wrap", gap: theme.spacing.md }}>
        {ordered.map((slot) => (
          <BadgeTile key={`${slot.achievementId}-${slot.level}`} slot={slot} />
        ))}
      </View>
    </Screen>
  );
}
