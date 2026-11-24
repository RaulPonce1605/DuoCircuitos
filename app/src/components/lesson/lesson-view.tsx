import Ionicons from "@expo/vector-icons/Ionicons";
import { useRouter } from "expo-router";
import { useTranslation } from "react-i18next";
import { ActivityIndicator, Pressable, View } from "react-native";

import { ExerciseRenderer } from "@/components/exercises/registry";
import { FeedbackPanel } from "@/components/lesson/feedback-panel";
import { AppText, Button, ProgressBar, Screen } from "@/components/ui";
import { useLessonSession } from "@/hooks/use-lesson-session";
import { useTheme } from "@/hooks/use-theme";
import { errorMessage } from "@/i18n/error-message";

export function LessonView({ lessonSlug }: { lessonSlug: string }) {
  const { t } = useTranslation();
  const theme = useTheme();
  const router = useRouter();
  const session = useLessonSession(lessonSlug);
  const { attempt, exercise, progress, feedback } = session;

  const exit = () => (router.canGoBack() ? router.back() : router.replace("/"));

  const onContinue = () => {
    const finishedAttempt = session.goNext();
    if (finishedAttempt) {
      router.replace({ pathname: "/leccion/resumen/[attemptId]", params: { attemptId: finishedAttempt } });
    }
  };

  const header = (
    <View style={{ flexDirection: "row", alignItems: "center", gap: theme.spacing.md }}>
      <Pressable
        onPress={exit}
        accessibilityRole="button"
        accessibilityLabel={t("lesson.exit")}
        hitSlop={theme.spacing.sm}
        style={{ minWidth: theme.sizes.touchTarget, minHeight: theme.sizes.touchTarget, justifyContent: "center" }}
      >
        <Ionicons name="close" size={theme.sizes.iconLg} color={theme.colors.textMuted} />
      </Pressable>
      <View style={{ flex: 1 }}>
        <ProgressBar
          progress={progress ? progress.completed / Math.max(progress.total, 1) : 0}
          accessibilityLabel={t("lesson.progress")}
        />
      </View>
    </View>
  );

  if (attempt.isPending) {
    return (
      <Screen>
        {header}
        <ActivityIndicator
          color={theme.colors.primary}
          accessibilityLabel={t("lesson.loading")}
          style={{ marginTop: theme.spacing.xxl }}
        />
      </Screen>
    );
  }

  if (attempt.isError || !exercise) {
    return (
      <Screen>
        {header}
        <AppText color="error" accessibilityRole="alert">
          {errorMessage(attempt.error)}
        </AppText>
        <Button label={t("common.retry")} variant="secondary" onPress={() => void attempt.refetch()} />
      </Screen>
    );
  }

  const footer = feedback ? (
    <View style={{ gap: theme.spacing.md }}>
      <FeedbackPanel result={feedback} />
      <Button
        label={t("lesson.continue")}
        variant={feedback.correct ? "success" : "danger"}
        onPress={onContinue}
      />
    </View>
  ) : (
    <View style={{ gap: theme.spacing.sm }}>
      {session.checkError ? (
        <AppText color="error" accessibilityRole="alert">
          {errorMessage(session.checkError)}
        </AppText>
      ) : null}
      <Button
        label={t("lesson.check")}
        onPress={session.checkAnswer}
        disabled={session.answer === null}
        loading={session.isChecking}
        accessibilityHint={session.answer === null ? t("lesson.chooseAnswer") : undefined}
      />
    </View>
  );

  return (
    <Screen scroll footer={footer}>
      {header}
      {/* La key reinicia el componente en cada ejercicio (y en cada reintento). */}
      <ExerciseRenderer
        key={exercise.instance_id}
        type={exercise.exercise.type}
        exercise={exercise.exercise}
        onAnswerChange={session.setAnswer}
        disabled={feedback !== null}
      />
    </Screen>
  );
}
