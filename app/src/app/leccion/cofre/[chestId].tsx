import { useLocalSearchParams, useRouter } from "expo-router";

import { ChestView } from "@/components/rewards/chest-view";

/** El cofre que dejó un intento; después va la pantalla de racha. */
export default function LessonChestScreen() {
  const { chestId, attemptId } = useLocalSearchParams<{ chestId: string; attemptId?: string }>();
  const router = useRouter();
  const onContinue = () =>
    attemptId
      ? router.replace({ pathname: "/leccion/racha/[attemptId]", params: { attemptId } })
      : router.replace("/");
  return <ChestView target={{ kind: "attempt", chestId }} onContinue={onContinue} />;
}
