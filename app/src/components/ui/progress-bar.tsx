import { View } from "react-native";

import { useTheme } from "@/hooks/use-theme";
import type { ColorTokens } from "@/theme";

type Props = {
  /** Avance entre 0 y 1; se recorta a ese rango. */
  progress: number;
  /** Texto para lectores de pantalla, ya traducido ("Progreso de la lección"). */
  accessibilityLabel: string;
  color?: keyof ColorTokens;
};

export function ProgressBar({ progress, accessibilityLabel, color = "primary" }: Props) {
  const theme = useTheme();
  const clamped = Number.isFinite(progress) ? Math.min(Math.max(progress, 0), 1) : 0;
  const percent = Math.round(clamped * 100);

  return (
    <View
      accessible
      accessibilityRole="progressbar"
      accessibilityLabel={accessibilityLabel}
      accessibilityValue={{ min: 0, max: 100, now: percent }}
      style={{
        height: theme.sizes.progressBar,
        borderRadius: theme.radii.pill,
        backgroundColor: theme.colors.surfaceMuted,
        overflow: "hidden",
      }}
    >
      <View
        testID="progress-fill"
        style={{
          width: `${percent}%`,
          height: "100%",
          borderRadius: theme.radii.pill,
          backgroundColor: theme.colors[color],
        }}
      />
    </View>
  );
}
