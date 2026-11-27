import Ionicons from "@expo/vector-icons/Ionicons";
import { useTranslation } from "react-i18next";
import { ActivityIndicator, View } from "react-native";

import { AppText, Button, Screen } from "@/components/ui";
import { useCurrentUser } from "@/hooks/use-current-user";
import { useLessonSummary } from "@/hooks/use-lesson-summary";
import { useTheme } from "@/hooks/use-theme";
import { errorMessage } from "@/i18n/error-message";

const FLAME_SIZE = 140;

type Props = {
  attemptId: string;
  onContinue: () => void;
};

/** Pantalla de racha al terminar la lección (CLAUDE.md 1.2). La racha la calcula el backend. */
export function StreakView({ attemptId, onContinue }: Props) {
  const { t } = useTranslation();
  const theme = useTheme();
  const summary = useLessonSummary(attemptId);
  const me = useCurrentUser();
  const footer = <Button label={t("streak.continue")} onPress={onContinue} />;

  if (summary.isPending) {
    return (
      <Screen footer={footer}>
        <ActivityIndicator
          color={theme.colors.streak}
          accessibilityLabel={t("streak.loading")}
          style={{ marginTop: theme.spacing.xxl }}
        />
      </Screen>
    );
  }
  if (summary.isError) {
    return (
      <Screen footer={footer}>
        <AppText color="error" accessibilityRole="alert">
          {errorMessage(summary.error)}
        </AppText>
      </Screen>
    );
  }

  const { streak, streak_extended: extended } = summary.data;
  const message = !extended ? t("streak.kept") : streak === 1 ? t("streak.start") : t("streak.up");
  return (
    <Screen footer={footer}>
      <View
        testID="streak-view"
        style={{ flex: 1, alignItems: "center", justifyContent: "center", gap: theme.spacing.md }}
      >
        <Ionicons name="flame" size={FLAME_SIZE} color={theme.colors.streak} />
        <AppText variant="display" color="streak" align="center" accessibilityRole="header">
          {t("streak.days", { count: streak })}
        </AppText>
        <AppText variant="subtitle" align="center">
          {message}
        </AppText>
        {me.data ? (
          <AppText color="textMuted" align="center">
            {t("streak.longest", { count: me.data.streak_longest })}
          </AppText>
        ) : null}
      </View>
    </Screen>
  );
}
