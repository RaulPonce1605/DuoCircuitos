import { useState } from "react";
import { useTranslation } from "react-i18next";
import { Pressable, View } from "react-native";

import type { ExerciseComponentProps } from "@/components/exercises/types";
import { AppText, TextField } from "@/components/ui";
import { useTheme } from "@/hooks/use-theme";

/** Prefijos SI que se ofrecen; el backend convierte a la unidad base al Comprobar. */
export const SI_PREFIXES = ["M", "k", "", "m", "µ", "n"] as const;

export function NumericAnswer({
  exercise,
  onAnswerChange,
  disabled,
}: ExerciseComponentProps<"numeric">) {
  const { t } = useTranslation();
  const theme = useTheme();
  const [value, setValue] = useState("");
  const [prefix, setPrefix] = useState<(typeof SI_PREFIXES)[number]>("");

  const emit = (nextValue: string, nextPrefix: string) => {
    onAnswerChange(
      nextValue.trim() === ""
        ? null
        : { type: "numeric", value: nextValue.trim(), unit: `${nextPrefix}${exercise.unit}` },
    );
  };

  return (
    <View style={{ gap: theme.spacing.md }}>
      <AppText variant="subtitle">{exercise.prompt}</AppText>
      <TextField
        label={t("exercise.numericLabel")}
        hint={t("exercise.numericHint")}
        value={value}
        onChangeText={(next) => {
          setValue(next);
          emit(next, prefix);
        }}
        editable={!disabled}
        keyboardType="decimal-pad"
        inputMode="decimal"
        maxLength={40}
      />
      <AppText variant="bodyStrong">{t("exercise.unitLabel")}</AppText>
      <View accessibilityRole="radiogroup" style={{ flexDirection: "row", flexWrap: "wrap", gap: theme.spacing.sm }}>
        {SI_PREFIXES.map((option) => {
          const unit = `${option}${exercise.unit}`;
          const selected = option === prefix;
          return (
            <Pressable
              key={unit}
              onPress={() => {
                setPrefix(option);
                emit(value, option);
              }}
              disabled={disabled}
              accessibilityRole="radio"
              accessibilityLabel={unit}
              accessibilityState={{ checked: selected, disabled }}
              style={{
                minWidth: theme.sizes.touchTarget,
                minHeight: theme.sizes.touchTarget,
                alignItems: "center",
                justifyContent: "center",
                paddingHorizontal: theme.spacing.sm,
                borderRadius: theme.radii.md,
                borderWidth: theme.borders.thick,
                borderColor: selected ? theme.colors.primary : theme.colors.border,
                backgroundColor: selected ? theme.colors.primarySoft : theme.colors.surface,
              }}
            >
              <AppText variant="bodyStrong" color={selected ? "primary" : "text"}>
                {unit}
              </AppText>
            </Pressable>
          );
        })}
      </View>
    </View>
  );
}
