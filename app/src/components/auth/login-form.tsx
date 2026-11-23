import { Link } from "expo-router";
import { useState } from "react";
import { useTranslation } from "react-i18next";
import { View } from "react-native";

import { looksLikeEmail } from "@/components/auth/validation";
import { AppText, Button, TextField } from "@/components/ui";
import { useSession } from "@/hooks/use-session";
import { useTheme } from "@/hooks/use-theme";
import { errorMessage } from "@/i18n/error-message";

export function LoginForm() {
  const { t } = useTranslation();
  const theme = useTheme();
  const { signIn } = useSession();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [submitted, setSubmitted] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [serverError, setServerError] = useState<string | null>(null);

  const emailError = submitted && !looksLikeEmail(email) ? t("auth.invalidEmail") : null;
  const passwordError = submitted && password.length === 0 ? t("auth.missingPassword") : null;

  const onSubmit = async () => {
    setSubmitted(true);
    setServerError(null);
    if (!looksLikeEmail(email) || password.length === 0) {
      return;
    }
    setSubmitting(true);
    try {
      await signIn(email, password);
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
          {t("auth.loginTitle")}
        </AppText>
        <AppText color="textMuted">{t("auth.loginSubtitle")}</AppText>
      </View>
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
        secureTextEntry
        autoComplete="current-password"
        textContentType="password"
        onSubmitEditing={onSubmit}
      />
      {serverError ? (
        <AppText color="error" accessibilityRole="alert">
          {serverError}
        </AppText>
      ) : null}
      <Button label={t("auth.login")} onPress={onSubmit} loading={submitting} />
      <Link href="/registro" style={{ alignSelf: "center", padding: theme.spacing.sm }}>
        <AppText color="primary" variant="bodyStrong">
          {t("auth.toRegister")}
        </AppText>
      </Link>
    </View>
  );
}
