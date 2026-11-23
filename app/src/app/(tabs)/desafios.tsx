import { useTranslation } from "react-i18next";

import { EmptyState } from "@/components/empty-state";
import { Screen } from "@/components/ui";

export default function ChallengesScreen() {
  const { t } = useTranslation();
  return (
    <Screen>
      <EmptyState icon="flag" title={t("challenges.title")} message={t("challenges.empty")} />
    </Screen>
  );
}
