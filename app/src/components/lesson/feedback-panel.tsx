import Ionicons from "@expo/vector-icons/Ionicons";
import { useTranslation } from "react-i18next";
import { View } from "react-native";

import { AppText } from "@/components/ui";
import { useTheme } from "@/hooks/use-theme";
import type { CheckResult } from "@/services/lesson-service";

/** Lo que respondió el backend al Comprobar: correcto o no, la respuesta y la explicación. */
export function FeedbackPanel({ result }: { result: CheckResult }) {
  const { t } = useTranslation();
  const theme = useTheme();
  const tone = result.correct ? "success" : "error";

  return (
    <View
      testID="feedback-panel"
      accessibilityLiveRegion="polite"
      style={{
        gap: theme.spacing.sm,
        padding: theme.spacing.md,
        borderRadius: theme.radii.lg,
        backgroundColor: theme.colors[result.correct ? "successSoft" : "errorSoft"],
      }}
    >
      <View style={{ flexDirection: "row", alignItems: "center", gap: theme.spacing.sm }}>
        <Ionicons
          name={result.correct ? "checkmark-circle" : "close-circle"}
          size={theme.sizes.iconMd}
          color={theme.colors[tone]}
        />
        <AppText variant="subtitle" color={tone} accessibilityRole="header">
          {result.correct ? t("lesson.correct") : t("lesson.incorrect")}
        </AppText>
      </View>
      {result.correct ? null : (
        <AppText variant="bodyStrong">
          {t("lesson.correctAnswer", { answer: result.correct_answer })}
        </AppText>
      )}
      <AppText>{result.explanation}</AppText>
      {result.correct ? null : (
        <AppText variant="caption" color="textMuted">
          {t("lesson.willRepeat")}
        </AppText>
      )}
    </View>
  );
}
