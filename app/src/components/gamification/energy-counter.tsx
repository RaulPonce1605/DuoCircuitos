import { useTranslation } from "react-i18next";

import { Counter } from "@/components/ui";
import { useNow } from "@/hooks/use-now";
import type { Energy } from "@/services/auth-service";

type Props = {
  energy: Energy;
  testID?: string;
};

function minutesUntil(isoDate: string, now: number): number {
  return Math.max(1, Math.ceil((new Date(isoDate).getTime() - now) / 60_000));
}

/** Energía que queda. El backend la calcula; aquí solo se muestra (CLAUDE.md 5.4). */
export function EnergyCounter({ energy, testID = "energy-counter" }: Props) {
  const { t } = useTranslation();
  const now = useNow();
  const label =
    energy.next_refill_at === null
      ? t("energy.full", { current: energy.current, max: energy.max })
      : t("energy.refilling", {
          current: energy.current,
          max: energy.max,
          count: minutesUntil(energy.next_refill_at, now),
        });
  return (
    <Counter
      testID={testID}
      icon={energy.current > 0 ? "battery-charging" : "battery-dead"}
      color={energy.current > 0 ? "energy" : "error"}
      value={energy.current}
      accessibilityLabel={label}
    />
  );
}
