import { Circle, G, Line, Path, Text as SvgText } from "react-native-svg";

import type { ExerciseOf } from "@/components/exercises/types";
import { fonts } from "@/theme";

export type DiagramElement = ExerciseOf<"circuit_diagram">["elements"][number];

/** Píxeles por unidad de la cuadrícula del temario y margen alrededor del dibujo. */
export const GRID = 64;
export const MARGIN = 40;
/** Tamaño máximo del símbolo dentro del segmento (el resto son terminales). */
const SYMBOL = 40;
/** Signos de la fuente y letras de los medidores: son parte del símbolo, no texto de la UI. */
const PLUS = "+";
const MINUS = "−";
const METER_LETTER = { ammeter: "A", voltmeter: "V" } as const;

type Point = { x: number; y: number };

export function toPixels({ x, y }: Point): Point {
  return { x: MARGIN + x * GRID, y: MARGIN + y * GRID };
}

/** Geometría de un elemento: inicio, largo y ángulo (los elementos son horizontales o verticales). */
export function segment(element: DiagramElement) {
  const start = toPixels(element.start);
  const end = toPixels(element.end);
  const dx = end.x - start.x;
  const dy = end.y - start.y;
  const length = Math.hypot(dx, dy);
  const angle = dx > 0 ? 0 : dx < 0 ? 180 : dy > 0 ? 90 : 270;
  const center = { x: (start.x + end.x) / 2, y: (start.y + end.y) / 2 };
  const unit = { x: dx / length, y: dy / length };
  return { start, end, length, angle, center, unit, horizontal: dy === 0 };
}

type SymbolProps = {
  element: DiagramElement;
  stroke: string;
  strokeWidth: number;
  textColor: string;
};

/**
 * Símbolo de un elemento, dibujado sobre el eje x de 0 a `length` y luego girado a su lugar.
 * Convención de las fuentes: `end` es el lado positivo (+) o hacia donde apunta la corriente.
 */
export function ElementSymbol({ element, stroke, strokeWidth, textColor }: SymbolProps) {
  const { start, length, angle, center, unit } = segment(element);
  const size = Math.min(SYMBOL, length - 8);
  const a = (length - size) / 2;
  const b = a + size;
  const mid = length / 2;
  const radius = size / 2;
  const common = { stroke, strokeWidth, fill: "none", strokeLinecap: "round" as const, strokeLinejoin: "round" as const };
  const leads = (
    <>
      <Line x1={0} y1={0} x2={a} y2={0} {...common} />
      <Line x1={b} y1={0} x2={length} y2={0} {...common} />
    </>
  );

  let body: React.ReactNode = null;
  let centered: React.ReactNode = null; // texto que no se gira (A, V, +, −)
  switch (element.kind) {
    case "wire":
      body = <Line x1={0} y1={0} x2={length} y2={0} {...common} />;
      break;
    case "resistor": {
      const step = size / 6;
      const zigzag = Array.from({ length: 6 }, (_, i) => `L ${a + step * (i + 0.5)} ${i % 2 === 0 ? -8 : 8}`).join(" ");
      body = (
        <>
          {leads}
          <Path d={`M ${a} 0 ${zigzag} L ${b} 0`} {...common} />
        </>
      );
      break;
    }
    case "capacitor":
      body = (
        <>
          <Line x1={0} y1={0} x2={mid - 4} y2={0} {...common} />
          <Line x1={mid + 4} y1={0} x2={length} y2={0} {...common} />
          <Line x1={mid - 4} y1={-12} x2={mid - 4} y2={12} {...common} />
          <Line x1={mid + 4} y1={-12} x2={mid + 4} y2={12} {...common} />
        </>
      );
      break;
    case "inductor": {
      const loop = size / 4;
      const arcs = Array.from({ length: 4 }, () => `a ${loop / 2} ${loop / 2} 0 0 1 ${loop} 0`).join(" ");
      body = (
        <>
          {leads}
          <Path d={`M ${a} 0 ${arcs}`} {...common} />
        </>
      );
      break;
    }
    case "switch":
      body = (
        <>
          {leads}
          <Circle cx={a} cy={0} r={2.5} fill={stroke} />
          <Circle cx={b} cy={0} r={2.5} fill={stroke} />
          <Line x1={a} y1={0} x2={b - 4} y2={-12} {...common} />
        </>
      );
      break;
    case "lamp": {
      const d = radius * Math.SQRT1_2;
      body = (
        <>
          {leads}
          <Circle cx={mid} cy={0} r={radius} {...common} />
          <Line x1={mid - d} y1={-d} x2={mid + d} y2={d} {...common} />
          <Line x1={mid - d} y1={d} x2={mid + d} y2={-d} {...common} />
        </>
      );
      break;
    }
    case "current_source":
      body = (
        <>
          {leads}
          <Circle cx={mid} cy={0} r={radius} {...common} />
          <Line x1={mid - radius / 2} y1={0} x2={mid + radius / 2} y2={0} {...common} />
          <Path d={`M ${mid + radius / 2 - 6} -5 L ${mid + radius / 2} 0 L ${mid + radius / 2 - 6} 5`} {...common} />
        </>
      );
      break;
    case "voltage_source":
    case "ammeter":
    case "voltmeter": {
      body = (
        <>
          {leads}
          <Circle cx={mid} cy={0} r={radius} {...common} />
        </>
      );
      const font = { fill: textColor, fontSize: 15, fontFamily: fonts.heading, textAnchor: "middle" as const };
      if (element.kind === "voltage_source") {
        const offset = radius / 2;
        centered = (
          <>
            <SvgText x={center.x + unit.x * offset} y={center.y + unit.y * offset + 5} {...font}>
              {PLUS}
            </SvgText>
            <SvgText x={center.x - unit.x * offset} y={center.y - unit.y * offset + 5} {...font}>
              {MINUS}
            </SvgText>
          </>
        );
      } else {
        centered = (
          <SvgText x={center.x} y={center.y + 5} {...font}>
            {METER_LETTER[element.kind]}
          </SvgText>
        );
      }
      break;
    }
  }

  return (
    <>
      <G transform={`translate(${start.x} ${start.y}) rotate(${angle})`}>{body}</G>
      {centered}
    </>
  );
}
