import type Ionicons from "@expo/vector-icons/Ionicons";
import type { ComponentProps } from "react";

type IconName = ComponentProps<typeof Ionicons>["name"];

/** Las 5 pestañas (CLAUDE.md 1.6), en orden. `name` es el archivo en `src/app/(tabs)/`. */
export const TAB_ROUTES = [
  { name: "index", titleKey: "tabs.home", icon: "home" },
  { name: "desafios", titleKey: "tabs.challenges", icon: "flag" },
  { name: "ligas", titleKey: "tabs.leagues", icon: "podium" },
  { name: "perfil", titleKey: "tabs.profile", icon: "person-circle" },
  { name: "mas", titleKey: "tabs.more", icon: "ellipsis-horizontal-circle" },
] as const satisfies readonly { name: string; titleKey: `tabs.${string}`; icon: IconName }[];
