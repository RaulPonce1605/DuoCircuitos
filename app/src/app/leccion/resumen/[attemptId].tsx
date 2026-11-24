import { useLocalSearchParams } from "expo-router";

import { SummaryView } from "@/components/lesson/summary-view";

export default function LessonSummaryScreen() {
  const { attemptId } = useLocalSearchParams<{ attemptId: string }>();
  return <SummaryView attemptId={attemptId} />;
}
