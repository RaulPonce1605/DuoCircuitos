import Ionicons from "@expo/vector-icons/Ionicons";
import { useState } from "react";
import { useTranslation } from "react-i18next";
import { Pressable, View } from "react-native";

import { AppText, Button, Card, TextField } from "@/components/ui";
import { type TutorChatMessage, useTutor } from "@/hooks/use-tutor";
import { useTheme } from "@/hooks/use-theme";
import { errorMessage } from "@/i18n/error-message";

type Props = {
  instanceId: string;
  onClose: () => void;
};

function Bubble({ message }: { message: TutorChatMessage }) {
  const { t } = useTranslation();
  const theme = useTheme();
  const fromTutor = message.role === "tutor";
  return (
    <View
      testID={`tutor-message-${message.role}`}
      style={{
        alignSelf: fromTutor ? "flex-start" : "flex-end",
        maxWidth: "90%",
        gap: theme.spacing.xxs,
        padding: theme.spacing.sm,
        borderRadius: theme.radii.md,
        backgroundColor: theme.colors[fromTutor ? "primarySoft" : "surfaceMuted"],
      }}
    >
      <AppText variant="caption" color="textMuted">
        {fromTutor
          ? message.source === "hint"
            ? t("tutor.fromSyllabus")
            : t("tutor.name")
          : t("tutor.you")}
      </AppText>
      <AppText>{message.text}</AppText>
    </View>
  );
}

/**
 * Panel "Pedir ayuda" (CLAUDE.md 1.4). La pista la decide el backend: aquí solo se manda la
 * pregunta (opcional) y se muestra la respuesta ya filtrada.
 */
export function TutorPanel({ instanceId, onClose }: Props) {
  const { t } = useTranslation();
  const theme = useTheme();
  const tutor = useTutor(instanceId);
  const [draft, setDraft] = useState("");

  const send = () => {
    tutor.ask(draft);
    setDraft("");
  };

  return (
    <Card testID="tutor-panel" borderTone="primary" style={{ gap: theme.spacing.md }}>
      <View style={{ flexDirection: "row", alignItems: "center", gap: theme.spacing.sm }}>
        <Ionicons name="bulb" size={theme.sizes.iconMd} color={theme.colors.primary} />
        <AppText variant="subtitle" accessibilityRole="header" style={{ flex: 1 }}>
          {t("tutor.title")}
        </AppText>
        <Pressable
          onPress={onClose}
          accessibilityRole="button"
          accessibilityLabel={t("tutor.close")}
          hitSlop={theme.spacing.sm}
        >
          <Ionicons name="chevron-down" size={theme.sizes.iconMd} color={theme.colors.textMuted} />
        </Pressable>
      </View>

      {tutor.messages.length === 0 ? (
        <AppText color="textMuted">{t("tutor.intro")}</AppText>
      ) : (
        <View accessibilityLiveRegion="polite" style={{ gap: theme.spacing.sm }}>
          {tutor.messages.map((message) => (
            <Bubble key={message.id} message={message} />
          ))}
        </View>
      )}

      {tutor.error ? (
        <AppText color="error" accessibilityRole="alert">
          {errorMessage(tutor.error)}
        </AppText>
      ) : null}

      {tutor.remaining === 0 ? (
        <AppText color="textMuted">{t("tutor.noMoreHelp")}</AppText>
      ) : (
        <>
          <TextField
            label={t("tutor.questionLabel")}
            hint={t("tutor.questionHint")}
            value={draft}
            onChangeText={setDraft}
            maxLength={500}
            onSubmitEditing={send}
            returnKeyType="send"
          />
          <Button
            label={tutor.messages.length === 0 ? t("tutor.ask") : t("tutor.askAgain")}
            variant="secondary"
            onPress={send}
            loading={tutor.isAsking}
            disabled={!tutor.canAsk}
          />
          {tutor.remaining !== null ? (
            <AppText variant="caption" color="textMuted" align="center">
              {t("tutor.remaining", { count: tutor.remaining })}
            </AppText>
          ) : null}
        </>
      )}
    </Card>
  );
}
