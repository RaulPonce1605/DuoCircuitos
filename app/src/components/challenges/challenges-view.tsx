import Ionicons from "@expo/vector-icons/Ionicons";
import type { ComponentProps } from "react";
import { useTranslation } from "react-i18next";
import { ActivityIndicator, View } from "react-native";

import { AppText, Button, Card, ProgressBar } from "@/components/ui";
import { useChallenges } from "@/hooks/use-challenges";
import { useNow } from "@/hooks/use-now";
import { useTheme } from "@/hooks/use-theme";
import { errorMessage } from "@/i18n/error-message";
import type { Challenge } from "@/services/challenges-service";

type IconName = ComponentProps<typeof Ionicons>["name"];

const KIND_ICON: Record<Challenge["kind"], IconName> = {
  earn_xp: "flash",
  complete_lessons: "book",
  first_try_correct: "locate",
  perfect_lessons: "star",
  open_chests: "gift",
};

const HOUR_MS = 3_600_000;

function ChallengeCard({ challenge }: { challenge: Challenge }) {
  const { t } = useTranslation();
  const theme = useTheme();
  const done = challenge.completed_at !== null;
  const name = t(`challenges.kind.${challenge.kind}`, { count: challenge.goal });
  return (
    <Card testID={`challenge-${challenge.kind}`} borderTone={done ? "success" : "border"} style={{ gap: theme.spacing.sm }}>
      <View style={{ flexDirection: "row", alignItems: "center", gap: theme.spacing.md }}>
        <Ionicons
          name={done ? "checkmark-circle" : KIND_ICON[challenge.kind]}
          size={theme.sizes.iconLg}
          color={theme.colors[done ? "success" : "primary"]}
        />
        <AppText variant="bodyStrong" style={{ flex: 1 }}>
          {name}
        </AppText>
        <View style={{ alignItems: "flex-end" }}>
          <AppText variant="bodyStrong" color="xp">
            {t("challenges.reward", { count: challenge.reward_xp })}
          </AppText>
          {challenge.reward_coins > 0 ? (
            <AppText variant="caption" color="coins">
              {t("challenges.rewardCoins", { count: challenge.reward_coins })}
            </AppText>
          ) : null}
        </View>
      </View>
      <ProgressBar
        progress={challenge.progress / challenge.goal}
        color={done ? "success" : "xp"}
        accessibilityLabel={t("challenges.progressLabel", { name })}
      />
      <AppText variant="caption" color={done ? "success" : "textMuted"} align="right">
        {done ? t("challenges.done") : t("challenges.progress", { progress: challenge.progress, goal: challenge.goal })}
      </AppText>
    </Card>
  );
}

function Section({ title, caption, challenges }: { title: string; caption: string; challenges: Challenge[] }) {
  const theme = useTheme();
  return (
    <View style={{ gap: theme.spacing.sm }}>
      <View style={{ flexDirection: "row", alignItems: "baseline", justifyContent: "space-between", gap: theme.spacing.sm }}>
        <AppText variant="subtitle" accessibilityRole="header">
          {title}
        </AppText>
        <AppText variant="caption" color="textMuted">
          {caption}
        </AppText>
      </View>
      {challenges.map((challenge) => (
        <ChallengeCard key={challenge.id} challenge={challenge} />
      ))}
    </View>
  );
}

/** Pestaña Desafíos: metas de hoy y del mes con barras de progreso. */
export function ChallengesView() {
  const { t } = useTranslation();
  const theme = useTheme();
  const query = useChallenges();
  const now = useNow();

  return (
    <View style={{ gap: theme.spacing.lg }}>
      <AppText variant="title" accessibilityRole="header">
        {t("challenges.title")}
      </AppText>
      {query.isPending ? (
        <ActivityIndicator
          color={theme.colors.primary}
          accessibilityLabel={t("challenges.loading")}
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
        <>
          {query.data.daily.length === 0 ? (
            <AppText color="textMuted">{t("challenges.empty")}</AppText>
          ) : (
            <Section
              title={t("challenges.daily")}
              caption={t("challenges.dailyEnds", {
                count: Math.max(1, Math.ceil((new Date(query.data.daily_ends_at).getTime() - now) / HOUR_MS)),
              })}
              challenges={query.data.daily}
            />
          )}
          {query.data.monthly.length > 0 ? (
            <Section
              title={t("challenges.monthly")}
              caption={t("challenges.monthlyEnds", {
                count: Math.max(1, Math.ceil((new Date(query.data.monthly_ends_at).getTime() - now) / (24 * HOUR_MS))),
              })}
              challenges={query.data.monthly}
            />
          ) : null}
        </>
      )}
    </View>
  );
}
