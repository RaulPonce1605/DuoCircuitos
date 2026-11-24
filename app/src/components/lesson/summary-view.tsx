import Ionicons from "@expo/vector-icons/Ionicons";
import { useRouter } from "expo-router";
import type { ComponentProps } from "react";
import { useTranslation } from "react-i18next";
import { ActivityIndicator, View } from "react-native";

import { AppText, Button, Card, Screen } from "@/components/ui";
import { useLessonSummary } from "@/hooks/use-lesson-summary";
import { useTheme } from "@/hooks/use-theme";
import { errorMessage } from "@/i18n/error-message";
import type { ColorTokens } from "@/theme";

type StatProps = {
  icon: ComponentProps<typeof Ionicons>["name"];
  color: keyof ColorTokens;
  label: string;
  value: string;
  testID: string;
};

function Stat({ icon, color, label, value, testID }: StatProps) {
  const theme = useTheme();
  return (
    <Card
      testID={testID}
      borderTone={color}
      style={{ flex: 1, minWidth: 140, alignItems: "center", gap: theme.spacing.xs }}
    >
      <View accessible accessibilityLabel={`${label}: ${value}`} style={{ alignItems: "center", gap: theme.spacing.xs }}>
        <AppText variant="caption" color="textMuted">
          {label}
        </AppText>
        <View style={{ flexDirection: "row", alignItems: "center", gap: theme.spacing.xs }}>
          <Ionicons name={icon} size={theme.sizes.iconMd} color={theme.colors[color]} />
          <AppText variant="title" color={color}>
            {value}
          </AppText>
        </View>
      </View>
    </Card>
  );
}

/** Resumen al terminar (CLAUDE.md 1.2): EXP, precisión, conceptos y racha. Todo del backend. */
export function SummaryView({ attemptId }: { attemptId: string }) {
  const { t } = useTranslation();
  const theme = useTheme();
  const router = useRouter();
  const summary = useLessonSummary(attemptId);

  if (summary.isPending) {
    return (
      <Screen>
        <ActivityIndicator
          color={theme.colors.primary}
          accessibilityLabel={t("summary.loading")}
          style={{ marginTop: theme.spacing.xxl }}
        />
      </Screen>
    );
  }

  const goHome = () => router.replace("/");

  if (summary.isError) {
    return (
      <Screen>
        <AppText color="error" accessibilityRole="alert">
          {errorMessage(summary.error)}
        </AppText>
        <Button label={t("common.retry")} variant="secondary" onPress={() => void summary.refetch()} />
        <Button label={t("summary.continue")} onPress={goHome} />
      </Screen>
    );
  }

  const data = summary.data;
  return (
    <Screen scroll footer={<Button label={t("summary.continue")} onPress={goHome} />}>
      <View style={{ alignItems: "center", gap: theme.spacing.sm, marginTop: theme.spacing.lg }}>
        <Ionicons name="trophy" size={theme.sizes.iconLg * 2} color={theme.colors.accent} />
        <AppText variant="display" align="center" accessibilityRole="header">
          {t("summary.title")}
        </AppText>
        <AppText color="textMuted" align="center">
          {data.lesson.title}
        </AppText>
      </View>

      <View style={{ flexDirection: "row", flexWrap: "wrap", gap: theme.spacing.md }}>
        <Stat
          testID="summary-xp"
          icon="flash"
          color="xp"
          label={t("summary.xp")}
          value={t("summary.xpValue", { count: data.xp_awarded })}
        />
        <Stat
          testID="summary-accuracy"
          icon="locate"
          color="primary"
          label={t("summary.accuracy")}
          value={t("summary.accuracyValue", { value: data.accuracy })}
        />
      </View>
      <AppText color="textMuted" align="center">
        {`${t("summary.firstTry")}: ${t("summary.firstTryValue", {
          correct: data.first_try_correct,
          total: data.exercise_count,
        })}`}
      </AppText>

      <Card borderTone="streak" testID="summary-streak">
        <View style={{ flexDirection: "row", alignItems: "center", gap: theme.spacing.md }}>
          <Ionicons name="flame" size={theme.sizes.iconLg} color={theme.colors.streak} />
          <View style={{ flex: 1, gap: theme.spacing.xxs }}>
            <AppText variant="subtitle" color="streak">
              {t("summary.streak", { count: data.streak })}
            </AppText>
            <AppText color="textMuted">
              {data.streak_extended ? t("summary.streakUp") : t("summary.streakKept")}
            </AppText>
          </View>
        </View>
      </Card>

      <Card>
        <AppText variant="subtitle" accessibilityRole="header" style={{ marginBottom: theme.spacing.sm }}>
          {t("summary.concepts")}
        </AppText>
        <View accessibilityRole="list" style={{ gap: theme.spacing.xs }}>
          {data.concepts.map((concept) => (
            <View key={concept} style={{ flexDirection: "row", alignItems: "center", gap: theme.spacing.sm }}>
              <Ionicons name="checkmark-circle" size={theme.sizes.iconSm} color={theme.colors.success} />
              <AppText>{concept}</AppText>
            </View>
          ))}
        </View>
      </Card>
    </Screen>
  );
}
