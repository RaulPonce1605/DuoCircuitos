import { useState } from "react";
import { useTranslation } from "react-i18next";
import { Pressable, View } from "react-native";
import Svg, { Circle, G, Rect, Text as SvgText } from "react-native-svg";

import {
  type DiagramElement,
  ElementSymbol,
  GRID,
  MARGIN,
  segment,
  toPixels,
} from "@/components/exercises/circuit_diagram/symbols";
import type { ExerciseComponentProps } from "@/components/exercises/types";
import { AppText } from "@/components/ui";
import { useTheme } from "@/hooks/use-theme";
import { fonts } from "@/theme";

/** Grosor del área que se puede tocar alrededor de cada elemento. */
const HIT = 40;
const LABEL_OFFSET = 30;

/** Espacio extra a la derecha para las etiquetas de los elementos verticales. */
const LABEL_SPACE = 32;

/** Rectángulo que se resalta y se puede tocar alrededor de un elemento (en coordenadas del SVG). */
function hitBox(element: DiagramElement) {
  const { center, horizontal, length } = segment(element);
  return {
    x: center.x - (horizontal ? length / 2 : HIT / 2),
    y: center.y - (horizontal ? HIT / 2 : length / 2),
    width: horizontal ? length : HIT,
    height: horizontal ? HIT : length,
  };
}

/** Puntos donde se juntan 3 o más terminales: ahí se dibuja un punto de unión. */
export function junctions(elements: DiagramElement[]): { x: number; y: number }[] {
  const counts = new Map<string, number>();
  for (const element of elements) {
    for (const { x, y } of [element.start, element.end]) {
      const key = `${x},${y}`;
      counts.set(key, (counts.get(key) ?? 0) + 1);
    }
  }
  return [...counts.entries()]
    .filter(([, count]) => count >= 3)
    .map(([key]) => {
      const [x, y] = key.split(",").map(Number);
      return { x, y };
    });
}

/**
 * Ejercicio de diagrama (CLAUDE.md 1.3): se tocan los elementos que pide el enunciado. Solo arma
 * la lista de elementos elegidos; cuáles son los correctos lo decide el backend.
 */
export function CircuitDiagram({ exercise, onAnswerChange, disabled }: ExerciseComponentProps<"circuit_diagram">) {
  const { t } = useTranslation();
  const theme = useTheme();
  const [selected, setSelected] = useState<string[]>([]);
  const [width, setWidth] = useState(0);

  const touchable = exercise.elements.filter((element) => element.kind !== "wire");
  const points = exercise.elements.flatMap((e) => [e.start, e.end]).concat(exercise.nodes.map((n) => n.point));
  // A la derecha queda espacio extra para las etiquetas de los elementos verticales.
  const viewWidth = Math.max(...points.map((p) => p.x)) * GRID + 2 * MARGIN + LABEL_SPACE;
  const viewHeight = Math.max(...points.map((p) => p.y)) * GRID + 2 * MARGIN;
  const drawWidth = Math.min(width, viewWidth * 1.5);
  const drawHeight = (drawWidth * viewHeight) / viewWidth;
  const scale = drawWidth / viewWidth;

  const toggle = (id: string) => {
    if (disabled) {
      return;
    }
    const next = selected.includes(id) ? selected.filter((x) => x !== id) : [...selected, id];
    setSelected(next);
    onAnswerChange(next.length > 0 ? { type: "circuit_diagram", elements: next } : null);
  };

  const describe = (element: DiagramElement) =>
    t("exercise.diagramElement", { label: element.label ?? "", kind: t(`exercise.diagramKinds.${element.kind}`) });

  return (
    <View style={{ gap: theme.spacing.md }}>
      <AppText variant="subtitle">{exercise.prompt}</AppText>

      <View
        testID="circuit-diagram"
        onLayout={(event) => setWidth(event.nativeEvent.layout.width)}
        importantForAccessibility="no-hide-descendants"
        accessibilityElementsHidden
        style={{
          backgroundColor: theme.colors.surface,
          borderRadius: theme.radii.md,
          borderWidth: theme.borders.thin,
          borderColor: theme.colors.border,
          alignItems: "center",
        }}
      >
        {drawWidth > 0 ? (
          <View style={{ width: drawWidth, height: drawHeight }}>
            <Svg width={drawWidth} height={drawHeight} viewBox={`0 0 ${viewWidth} ${viewHeight}`}>
              {exercise.elements.map((element) => {
                const isSelected = selected.includes(element.id);
                const { center, horizontal } = segment(element);
                return (
                  <G key={element.id}>
                    {isSelected ? (
                      <Rect {...hitBox(element)} rx={theme.radii.sm} fill={theme.colors.primarySoft} />
                    ) : null}
                    <ElementSymbol
                      element={element}
                      stroke={isSelected ? theme.colors.primary : theme.colors.text}
                      strokeWidth={isSelected ? 3.5 : 2.5}
                      textColor={isSelected ? theme.colors.primary : theme.colors.text}
                    />
                    {element.label ? (
                      <SvgText
                        x={center.x + (horizontal ? 0 : LABEL_OFFSET)}
                        y={center.y + (horizontal ? -LABEL_OFFSET + 6 : 5)}
                        fill={isSelected ? theme.colors.primary : theme.colors.textMuted}
                        fontSize={15}
                        fontFamily={fonts.heading}
                        textAnchor={horizontal ? "middle" : "start"}
                      >
                        {element.label}
                      </SvgText>
                    ) : null}
                  </G>
                );
              })}
              {junctions(exercise.elements).map((junction) => {
                const point = toPixels(junction);
                return <Circle key={`j-${junction.x}-${junction.y}`} cx={point.x} cy={point.y} r={4} fill={theme.colors.text} />;
              })}
              {exercise.nodes.map((node) => {
                const point = toPixels(node.point);
                return (
                  <G key={`n-${node.label}`}>
                    <Circle cx={point.x} cy={point.y} r={5} fill={theme.colors.surface} stroke={theme.colors.text} strokeWidth={2} />
                    <SvgText x={point.x + 10} y={point.y + 5} fill={theme.colors.accent} fontSize={16} fontFamily={fonts.heading}>
                      {node.label}
                    </SvgText>
                  </G>
                );
              })}
            </Svg>
            {/* Zonas táctiles encima del dibujo: los toques en el SVG no funcionan en web. */}
            {touchable.map((element) => {
              const box = hitBox(element);
              return (
                <Pressable
                  key={element.id}
                  testID={`diagram-hit-${element.id}`}
                  onPress={() => toggle(element.id)}
                  disabled={disabled}
                  style={{
                    position: "absolute",
                    left: box.x * scale,
                    top: box.y * scale,
                    width: box.width * scale,
                    height: box.height * scale,
                  }}
                />
              );
            })}
          </View>
        ) : null}
      </View>

      {/* La misma selección como lista: para lectores de pantalla y para quien prefiera tocar texto. */}
      <View style={{ gap: theme.spacing.xs }}>
        <AppText variant="caption" color="textMuted">
          {t("exercise.diagramHint")}
        </AppText>
        <View style={{ flexDirection: "row", flexWrap: "wrap", gap: theme.spacing.sm }}>
          {touchable.map((element) => {
            const isSelected = selected.includes(element.id);
            return (
              <Pressable
                key={element.id}
                onPress={() => toggle(element.id)}
                disabled={disabled}
                accessibilityRole="checkbox"
                accessibilityLabel={describe(element)}
                accessibilityState={{ checked: isSelected, disabled }}
                style={{
                  minHeight: theme.sizes.touchTarget,
                  justifyContent: "center",
                  paddingHorizontal: theme.spacing.md,
                  borderRadius: theme.radii.pill,
                  borderWidth: theme.borders.thick,
                  borderColor: isSelected ? theme.colors.primary : theme.colors.border,
                  backgroundColor: isSelected ? theme.colors.primarySoft : theme.colors.surface,
                }}
              >
                <AppText variant="bodyStrong" color={isSelected ? "primary" : "text"}>
                  {element.label}
                </AppText>
              </Pressable>
            );
          })}
        </View>
      </View>
    </View>
  );
}
