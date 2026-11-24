import { useState } from "react";
import { useTranslation } from "react-i18next";
import { View } from "react-native";

import type { ExerciseComponentProps } from "@/components/exercises/types";
import { AppText, TextField } from "@/components/ui";
import { useTheme } from "@/hooks/use-theme";

/** El hueco "___" no debe quedar solo en otra línea: se une con espacio no separable. */
export function keepBlankTogether(prompt: string): string {
  return prompt.replace(/ (?=_{2,})/g, " ");
}

export function FillPattern({
  exercise,
  onAnswerChange,
  disabled,
}: ExerciseComponentProps<"fill_pattern">) {
  const { t } = useTranslation();
  const theme = useTheme();
  const [text, setText] = useState("");

  const change = (value: string) => {
    setText(value);
    onAnswerChange(value.trim() === "" ? null : { type: "fill_pattern", text: value });
  };

  return (
    <View style={{ gap: theme.spacing.md }}>
      <AppText variant="subtitle">{keepBlankTogether(exercise.prompt)}</AppText>
      <TextField
        label={t("exercise.fillLabel")}
        value={text}
        onChangeText={change}
        editable={!disabled}
        autoCapitalize="none"
        autoCorrect={false}
        maxLength={200}
      />
    </View>
  );
}
