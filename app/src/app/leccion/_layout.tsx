import { Redirect, Stack } from "expo-router";

import { useSession } from "@/hooks/use-session";

export default function LessonLayout() {
  const { status } = useSession();
  if (status !== "signedIn") {
    return <Redirect href="/login" />;
  }
  return <Stack screenOptions={{ headerShown: false }} />;
}
