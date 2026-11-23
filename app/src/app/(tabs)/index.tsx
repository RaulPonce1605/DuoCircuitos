import { useTranslation } from "react-i18next";

import { EmptyState } from "@/components/empty-state";
import { Screen } from "@/components/ui";

export default function HomeScreen() {
  const { t } = useTranslation();
  return (
    <Screen>
      <EmptyState icon="home" title={t("home.title")} message={t("home.empty")} />
    </Screen>
  );
}
