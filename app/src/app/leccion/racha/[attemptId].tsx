import { useLocalSearchParams, useRouter } from "expo-router";

import { StreakView } from "@/components/rewards/streak-view";

export default function StreakScreen() {
  const { attemptId } = useLocalSearchParams<{ attemptId: string }>();
  const router = useRouter();
  return <StreakView attemptId={attemptId} onContinue={() => router.replace("/")} />;
}
