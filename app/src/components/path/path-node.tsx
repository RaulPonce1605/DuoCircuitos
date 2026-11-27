import Ionicons from "@expo/vector-icons/Ionicons";
import type { ComponentProps } from "react";
import { useTranslation } from "react-i18next";
import { Pressable, View } from "react-native";

import { AppText } from "@/components/ui";
import { useTheme } from "@/hooks/use-theme";
import type { PathNode as PathNodeData } from "@/services/path-service";
import type { ColorTokens } from "@/theme";

type IconName = ComponentProps<typeof Ionicons>["name"];

const TYPE_ICON: Record<PathNodeData["type"], IconName> = {
  lesson: "flash",
  review: "refresh",
  chest: "gift",
  assessment: "ribbon",
};

const NODE_SIZE = 64;


type Props = {
  node: PathNodeData;
  /** Al tocar un nodo desbloqueado; `type` dice si se juega o (el cofre) se abre. */
  onOpenNode: (nodeKey: string, type: PathNodeData["type"]) => void;
};

export function PathNode({ node, onOpenNode }: Props) {
  const { t } = useTranslation();
  const theme = useTheme();
  const playable = node.status !== "locked";

  const title = node.lesson?.title ?? t(`path.nodeType.${node.type}`);
  const statusText =
    node.status === "locked"
      ? t("path.status.locked")
      : node.status === "completed"
          ? t("path.status.completed")
          : t("path.status.available");

  const fill: keyof ColorTokens =
    node.status === "completed" ? "success" : node.status === "available" ? "primary" : "surfaceMuted";
  const iconColor: keyof ColorTokens = node.status === "locked" ? "locked" : "textOnPrimary";
  const icon: IconName =
    node.status === "locked" ? "lock-closed" : node.status === "completed" ? "checkmark" : TYPE_ICON[node.type];

  return (
    <Pressable
      testID={`path-node-${node.key}`}
      disabled={!playable}
      onPress={() => onOpenNode(node.key, node.type)}
      accessibilityRole="button"
      accessibilityLabel={`${title}, ${statusText}`}
      accessibilityState={{ disabled: !playable, selected: node.is_current }}
      style={({ pressed }) => ({
        flexDirection: "row",
        alignItems: "center",
        gap: theme.spacing.md,
        opacity: pressed ? 0.8 : 1,
      })}
    >
      <View
        style={{
          width: NODE_SIZE,
          height: NODE_SIZE,
          borderRadius: theme.radii.pill,
          backgroundColor: theme.colors[fill],
          borderWidth: node.is_current ? theme.borders.thick * 2 : theme.borders.thick,
          borderColor: node.is_current ? theme.colors.accent : theme.colors.border,
          alignItems: "center",
          justifyContent: "center",
        }}
      >
        <Ionicons name={icon} size={theme.sizes.iconLg} color={theme.colors[iconColor]} />
      </View>
      <View style={{ flex: 1, gap: theme.spacing.xxs }}>
        <AppText variant="bodyStrong" color={node.status === "locked" ? "textMuted" : "text"}>
          {title}
        </AppText>
        <AppText variant="caption" color={node.is_current ? "accent" : "textMuted"}>
          {node.is_current ? t("path.status.current") : statusText}
        </AppText>
      </View>
    </Pressable>
  );
}

export const PATH_NODE_SIZE = NODE_SIZE;
