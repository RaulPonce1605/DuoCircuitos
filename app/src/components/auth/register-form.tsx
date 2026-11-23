import { Link } from "expo-router";
import { useState } from "react";
import { useTranslation } from "react-i18next";
import { View } from "react-native";

import { looksLikeEmail, MIN_PASSWORD_LENGTH } from "@/components/auth/validation";
import { AppText, Button, TextField } from "@/components/ui";
import { useSession } from "@/hooks/use-session";
import { useTheme } from "@/hooks/use-theme";
import { errorMessage } from "@/i18n/error-message";

export function RegisterForm() {
  const { t } = useTranslation();
  const theme = useTheme();
  const { signUp } = useSession();
  const [displayName, setDisplayName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [submitted, setSubmitted] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [serverError, setServerError] = useState<string | null>(null);

  const nameError = submitted && displayName.trim() === "" ? t("auth.missingName") : null;
  const emailError = submitted && !looksLikeEmail(email) ? t("auth.invalidEmail") : null;
  const passwordError =
    submitted && password.length < MIN_PASSWORD_LENGTH ? t("auth.shortPassword") : null;

  const onSubmit = async () => {
    setSubmitted(true);
    setServerError(null);
    if (
      displayName.trim() === "" ||
      !looksLikeEmail(email) ||
      password.length < MIN_PASSWORD_LENGTH
    ) {
      return;
    }
    setSubmitting(true);
    try {
      await signUp({ email, password, displayName });
    } catch (error) {
      setServerError(errorMessage(error));
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <View style={{ gap: theme.spacing.md }}>
      <View style={{ gap: theme.spacing.xs }}>
        <AppText variant="title" accessibilityRole="header">
          {t("auth.registerTitle")}
        </AppText>
        <AppText color="textMuted">{t("auth.registerSubtitle")}</AppText>
      </View>
      <TextField
        label={t("auth.displayName")}
        value={displayName}
        onChangeText={setDisplayName}
        error={nameError}
        autoComplete="name"
        textContentType="name"
        maxLength={50}
      />
      <TextField
        label={t("auth.email")}
        value={email}
        onChangeText={setEmail}
        error={emailError}
        autoCapitalize="none"
        autoComplete="email"
        keyboardType="email-address"
        inputMode="email"
        textContentType="emailAddress"
      />
      <TextField
        label={t("auth.password")}
        value={password}
        onChangeText={setPassword}
        error={passwordError}
        hint={t("auth.passwordHint")}
        secureTextEntry
        autoComplete="new-password"
        textContentType="newPassword"
        maxLength={128}
        onSubmitEditing={onSubmit}
      />
      {serverError ? (
        <AppText color="error" accessibilityRole="alert">
          {serverError}
        </AppText>
      ) : null}
      <Button label={t("auth.register")} onPress={onSubmit} loading={submitting} />
      <Link href="/login" style={{ alignSelf: "center", padding: theme.spacing.sm }}>
        <AppText color="primary" variant="bodyStrong">
          {t("auth.toLogin")}
        </AppText>
      </Link>
    </View>
  );
}
