import { useTranslation } from "react-i18next";

import { EmptyState } from "@/components/empty-state";
import { Screen } from "@/components/ui";

export default function MoreScreen() {
  const { t } = useTranslation();
  return (
    <Screen>
      <EmptyState icon="ellipsis-horizontal-circle" title={t("more.title")} message={t("more.empty")} />
    </Screen>
  );
}
