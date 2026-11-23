import { useTranslation } from "react-i18next";

import { EmptyState } from "@/components/empty-state";
import { Screen } from "@/components/ui";

export default function ProfileScreen() {
  const { t } = useTranslation();
  return (
    <Screen>
      <EmptyState icon="person-circle" title={t("profile.title")} message={t("profile.empty")} />
    </Screen>
  );
}
