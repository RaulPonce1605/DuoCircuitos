import { useLocalSearchParams, useRouter } from "expo-router";

import { ChestView } from "@/components/rewards/chest-view";

/** El nodo cofre del camino. */
export default function PathChestScreen() {
  const { key } = useLocalSearchParams<{ key: string }>();
  const router = useRouter();
  return <ChestView key={key} target={{ kind: "node", nodeKey: key }} onContinue={() => router.replace("/")} />;
}
