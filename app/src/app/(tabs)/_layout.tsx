import Ionicons from "@expo/vector-icons/Ionicons";
import { Redirect, Tabs } from "expo-router";
import { useTranslation } from "react-i18next";

import { RemindersManager } from "@/components/reminders-manager";
import { TAB_ROUTES } from "@/components/tab-routes";
import { useSession } from "@/hooks/use-session";
import { useTheme } from "@/hooks/use-theme";
import { fonts } from "@/theme";

export default function TabsLayout() {
  const { t } = useTranslation();
  const theme = useTheme();
  const { status } = useSession();

  if (status !== "signedIn") {
    return <Redirect href="/login" />;
  }
  return (
    <>
    <RemindersManager />
    <Tabs
      screenOptions={{
        headerShown: false,
        tabBarActiveTintColor: theme.colors.primary,
        tabBarInactiveTintColor: theme.colors.textMuted,
        tabBarStyle: {
          backgroundColor: theme.colors.surface,
          borderTopColor: theme.colors.border,
        },
        tabBarLabelStyle: { fontFamily: fonts.headingMedium },
      }}
    >
      {TAB_ROUTES.map((tab) => (
        <Tabs.Screen
          key={tab.name}
          name={tab.name}
          options={{
            title: t(tab.titleKey),
            tabBarIcon: ({ color, size }) => (
              <Ionicons
                name={tab.icon}
                color={typeof color === "string" ? color : theme.colors.textMuted}
                size={size}
              />
            ),
          }}
        />
      ))}
    </Tabs>
    </>
  );
}
