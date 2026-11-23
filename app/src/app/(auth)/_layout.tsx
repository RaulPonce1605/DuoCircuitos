import { Redirect, Stack } from "expo-router";

import { useSession } from "@/hooks/use-session";

export default function AuthLayout() {
  const { status } = useSession();
  if (status === "signedIn") {
    return <Redirect href="/" />;
  }
  return <Stack screenOptions={{ headerShown: false }} />;
}
