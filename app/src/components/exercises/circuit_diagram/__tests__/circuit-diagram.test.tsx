import { fireEvent, render, screen } from "@testing-library/react-native";

import { AppProviders } from "@/components/app-providers";
import { CircuitDiagram, junctions } from "@/components/exercises/circuit_diagram/circuit-diagram";
import type { ExerciseOf } from "@/components/exercises/types";
import es from "@/i18n/es.json";

const EXERCISE: ExerciseOf<"circuit_diagram"> = {
  type: "circuit_diagram",
  prompt: "Toca los dos resistores que están en paralelo entre sí.",
  elements: [
    { id: "v1", kind: "voltage_source", start: { x: 0, y: 2 }, end: { x: 0, y: 0 }, label: "V1" },
    { id: "w1", kind: "wire", start: { x: 0, y: 0 }, end: { x: 1, y: 0 }, label: null },
    { id: "r1", kind: "resistor", start: { x: 1, y: 0 }, end: { x: 3, y: 0 }, label: "R1" },
    { id: "w2", kind: "wire", start: { x: 3, y: 0 }, end: { x: 4, y: 0 }, label: null },
    { id: "r2", kind: "resistor", start: { x: 4, y: 0 }, end: { x: 4, y: 2 }, label: "R2" },
    { id: "w3", kind: "wire", start: { x: 4, y: 0 }, end: { x: 6, y: 0 }, label: null },
    { id: "r3", kind: "resistor", start: { x: 6, y: 0 }, end: { x: 6, y: 2 }, label: "R3" },
    { id: "w4", kind: "wire", start: { x: 6, y: 2 }, end: { x: 4, y: 2 }, label: null },
    { id: "w5", kind: "wire", start: { x: 4, y: 2 }, end: { x: 0, y: 2 }, label: null },
  ],
  nodes: [{ point: { x: 6, y: 0 }, label: "a" }],
};

async function renderDiagram(onAnswerChange = jest.fn(), disabled = false) {
  await render(
    <AppProviders>
      <CircuitDiagram exercise={EXERCISE} onAnswerChange={onAnswerChange} disabled={disabled} />
    </AppProviders>,
  );
  // En las pruebas no hay medidas de pantalla: se simula el ancho del contenedor.
  await fireEvent(screen.getByTestId("circuit-diagram", { includeHiddenElements: true }), "layout", { nativeEvent: { layout: { width: 400 } } });
  return onAnswerChange;
}

describe("CircuitDiagram", () => {
  it("lista solo los elementos que se pueden tocar (sin cables)", async () => {
    await renderDiagram();

    expect(screen.getByText(EXERCISE.prompt)).toBeOnTheScreen();
    const boxes = screen.getAllByRole("checkbox");
    expect(boxes.map((box) => box.props.accessibilityLabel)).toEqual([
      "V1 (fuente de voltaje)",
      "R1 (resistor)",
      "R2 (resistor)",
      "R3 (resistor)",
    ]);
  });

  it("arma la respuesta con los elementos elegidos y se puede deseleccionar", async () => {
    const onAnswerChange = await renderDiagram();

    await fireEvent.press(screen.getByRole("checkbox", { name: "R2 (resistor)" }));
    await fireEvent.press(screen.getByRole("checkbox", { name: "R3 (resistor)" }));
    expect(screen.getByRole("checkbox", { name: "R2 (resistor)" })).toBeChecked();
    expect(onAnswerChange).toHaveBeenLastCalledWith({ type: "circuit_diagram", elements: ["r2", "r3"] });

    await fireEvent.press(screen.getByRole("checkbox", { name: "R2 (resistor)" }));
    await fireEvent.press(screen.getByRole("checkbox", { name: "R3 (resistor)" }));
    expect(onAnswerChange).toHaveBeenLastCalledWith(null);
  });

  it("tocar el elemento en el dibujo también lo elige", async () => {
    const onAnswerChange = await renderDiagram();

    await fireEvent.press(screen.getByTestId("diagram-hit-r2", { includeHiddenElements: true }));

    expect(onAnswerChange).toHaveBeenLastCalledWith({ type: "circuit_diagram", elements: ["r2"] });
    expect(screen.getByRole("checkbox", { name: "R2 (resistor)" })).toBeChecked();
    // Los cables no se pueden tocar.
    expect(screen.queryByTestId("diagram-hit-w1", { includeHiddenElements: true })).toBeNull();
  });

  it("después de Comprobar no deja cambiar la selección", async () => {
    const onAnswerChange = await renderDiagram(jest.fn(), true);

    await fireEvent.press(screen.getByRole("checkbox", { name: "R1 (resistor)" }));

    expect(onAnswerChange).not.toHaveBeenCalled();
    expect(screen.getByText(es.exercise.diagramHint)).toBeOnTheScreen();
  });

  it("marca uniones donde se juntan 3 o más terminales", () => {
    expect(junctions(EXERCISE.elements)).toEqual([
      { x: 4, y: 0 },
      { x: 4, y: 2 },
    ]);
  });
});
