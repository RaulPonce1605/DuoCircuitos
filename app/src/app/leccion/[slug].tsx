import { useTranslation } from "react-i18next";

import { EmptyState } from "@/components/empty-state";
import { Screen } from "@/components/ui";

// Marcador: la pantalla de lección completa llega en su propio PR.
export default function LessonScreen() {
  const { t } = useTranslation();
  return (
    <Screen>
      <EmptyState icon="flash" title={t("path.nodeType.lesson")} message={t("common.comingSoon")} />
    </Screen>
  );
}
