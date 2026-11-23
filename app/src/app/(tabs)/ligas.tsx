import { useTranslation } from "react-i18next";

import { EmptyState } from "@/components/empty-state";
import { Screen } from "@/components/ui";

export default function LeaguesScreen() {
  const { t } = useTranslation();
  return (
    <Screen>
      <EmptyState icon="podium" title={t("leagues.title")} message={t("leagues.empty")} />
    </Screen>
  );
}
