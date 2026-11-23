import { useState } from "react";
import { Pressable, View } from "react-native";

import type { ExerciseComponentProps } from "@/components/exercises/types";
import { AppText } from "@/components/ui";
import { useTheme } from "@/hooks/use-theme";

export function MultipleChoice({
  exercise,
  onAnswerChange,
  disabled,
}: ExerciseComponentProps<"multiple_choice">) {
  const theme = useTheme();
  const [selected, setSelected] = useState<number | null>(null);

  const choose = (index: number) => {
    setSelected(index);
    onAnswerChange({ type: "multiple_choice", option: index });
  };

  return (
    <View style={{ gap: theme.spacing.md }}>
      <AppText variant="subtitle">{exercise.prompt}</AppText>
      <View accessibilityRole="radiogroup" style={{ gap: theme.spacing.sm }}>
        {exercise.options.map((option, index) => {
          const isSelected = selected === index;
          return (
            <Pressable
              key={option}
              onPress={() => choose(index)}
              disabled={disabled}
              accessibilityRole="radio"
              accessibilityLabel={option}
              accessibilityState={{ checked: isSelected, disabled }}
              style={({ pressed }) => ({
                minHeight: theme.sizes.touchTarget,
                justifyContent: "center",
                paddingHorizontal: theme.spacing.md,
                paddingVertical: theme.spacing.sm,
                borderRadius: theme.radii.md,
                borderWidth: theme.borders.thick,
                borderColor: isSelected ? theme.colors.primary : theme.colors.border,
                backgroundColor: isSelected
                  ? theme.colors.primarySoft
                  : pressed
                    ? theme.colors.surfaceMuted
                    : theme.colors.surface,
              })}
            >
              <AppText color={isSelected ? "primary" : "text"} variant={isSelected ? "bodyStrong" : "body"}>
                {option}
              </AppText>
            </Pressable>
          );
        })}
      </View>
    </View>
  );
}
