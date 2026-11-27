import { View } from "react-native";

import { PATH_NODE_SIZE, PathNode } from "@/components/path/path-node";
import { AppText, Card } from "@/components/ui";
import { useTheme } from "@/hooks/use-theme";
import type { PathUnit } from "@/services/path-service";

type Props = {
  unit: PathUnit;
  onOpenNode: (nodeKey: string, type: PathUnit["nodes"][number]["type"]) => void;
};

/** Una unidad dibujada como un circuito: los nodos unidos por una pista de cobre. */
export function UnitCard({ unit, onOpenNode }: Props) {
  const theme = useTheme();
  return (
    <Card>
      <AppText variant="subtitle" accessibilityRole="header" style={{ marginBottom: theme.spacing.md }}>
        {unit.title}
      </AppText>
      {unit.nodes.map((node, index) => {
        const next = unit.nodes[index + 1];
        const traceLit = node.status === "completed" && next !== undefined && next.status !== "locked";
        return (
          <View key={node.key}>
            <PathNode node={node} onOpenNode={onOpenNode} />
            {next ? (
              <View
                testID={`trace-${node.key}`}
                style={{
                  width: theme.borders.thick * 2,
                  height: theme.spacing.lg,
                  marginLeft: PATH_NODE_SIZE / 2 - theme.borders.thick,
                  backgroundColor: traceLit ? theme.colors.accent : theme.colors.border,
                }}
              />
            ) : null}
          </View>
        );
      })}
    </Card>
  );
}
