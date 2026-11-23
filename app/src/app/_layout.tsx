import { AppProviders } from "@/components/app-providers";
import { RootNavigator } from "@/components/root-navigator";
import { SessionProvider } from "@/hooks/use-session";

export default function RootLayout() {
  return (
    <AppProviders>
      <SessionProvider>
        <RootNavigator />
      </SessionProvider>
    </AppProviders>
  );
}
