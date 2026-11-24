import { fireEvent, render, screen } from "@testing-library/react-native";

import { AppProviders } from "@/components/app-providers";
import { FillPattern, keepBlankTogether } from "@/components/exercises/fill_pattern/fill-pattern";
import { MultipleChoice } from "@/components/exercises/multiple_choice/multiple-choice";
import { NumericAnswer } from "@/components/exercises/numeric/numeric-answer";
import { ExerciseRenderer, exerciseRegistry } from "@/components/exercises/registry";
import type { ExercisePublic } from "@/components/exercises/types";
import es from "@/i18n/es.json";

const MC = {
  type: "multiple_choice" as const,
  prompt: "¿En qué unidad se mide la resistencia?",
  options: ["Volt", "Ohm", "Ampere"],
};
const FILL = { type: "fill_pattern" as const, prompt: "V = I · ___" };
const NUM = {
  type: "numeric" as const,
  prompt: "Un resistor de 220 Ω se conecta a 5 V. ¿Qué corriente circula?",
  unit: "A",
};

async function renderWith(node: React.ReactElement) {
  await render(<AppProviders>{node}</AppProviders>);
}

describe("registro", () => {
  it("tiene un componente para cada tipo del backend", () => {
    expect(Object.keys(exerciseRegistry).sort()).toEqual(["fill_pattern", "multiple_choice", "numeric"]);
  });

  it.each<ExercisePublic>([MC, FILL, NUM])("renderiza $type con su componente", async (exercise) => {
    await renderWith(
      <ExerciseRenderer type={exercise.type} exercise={exercise} onAnswerChange={jest.fn()} disabled={false} />,
    );
    expect(screen.getByText(exercise.prompt.replace(/ (?=_{2,})/g, " "))).toBeOnTheScreen();
  });
});

describe("MultipleChoice", () => {
  it("avisa el índice de la opción elegida y la marca", async () => {
    const onAnswerChange = jest.fn();
    await renderWith(<MultipleChoice exercise={MC} onAnswerChange={onAnswerChange} disabled={false} />);

    await fireEvent.press(screen.getByRole("radio", { name: "Ohm" }));

    expect(onAnswerChange).toHaveBeenLastCalledWith({ type: "multiple_choice", option: 1 });
    expect(screen.getByRole("radio", { name: "Ohm" })).toBeChecked();
    expect(screen.getByRole("radio", { name: "Volt" })).not.toBeChecked();
  });

  it("no cambia después de Comprobar", async () => {
    const onAnswerChange = jest.fn();
    await renderWith(<MultipleChoice exercise={MC} onAnswerChange={onAnswerChange} disabled />);

    await fireEvent.press(screen.getByRole("radio", { name: "Ohm" }));
    expect(onAnswerChange).not.toHaveBeenCalled();
  });
});

describe("FillPattern", () => {
  it("el hueco no se separa de la palabra anterior", () => {
    expect(keepBlankTogether("V = I · ___")).toBe("V = I · ___");
    expect(keepBlankTogether("la ___ es la misma")).toBe("la ___ es la misma");
  });

  it("manda el texto y null si queda vacío", async () => {
    const onAnswerChange = jest.fn();
    await renderWith(<FillPattern exercise={FILL} onAnswerChange={onAnswerChange} disabled={false} />);
    const input = screen.getByLabelText(es.exercise.fillLabel);

    await fireEvent.changeText(input, "R");
    expect(onAnswerChange).toHaveBeenLastCalledWith({ type: "fill_pattern", text: "R" });

    await fireEvent.changeText(input, "   ");
    expect(onAnswerChange).toHaveBeenLastCalledWith(null);
  });
});

describe("NumericAnswer", () => {
  it("arma valor y unidad con el prefijo elegido", async () => {
    const onAnswerChange = jest.fn();
    await renderWith(<NumericAnswer exercise={NUM} onAnswerChange={onAnswerChange} disabled={false} />);

    await fireEvent.changeText(screen.getByLabelText(es.exercise.numericLabel), "22.7");
    expect(onAnswerChange).toHaveBeenLastCalledWith({ type: "numeric", value: "22.7", unit: "A" });

    await fireEvent.press(screen.getByRole("radio", { name: "mA" }));
    expect(onAnswerChange).toHaveBeenLastCalledWith({ type: "numeric", value: "22.7", unit: "mA" });
    expect(screen.getByRole("radio", { name: "mA" })).toBeChecked();
  });

  it("ofrece los prefijos sobre la unidad del ejercicio", async () => {
    await renderWith(<NumericAnswer exercise={NUM} onAnswerChange={jest.fn()} disabled={false} />);

    for (const unit of ["MA", "kA", "A", "mA", "µA", "nA"]) {
      expect(screen.getByRole("radio", { name: unit })).toBeOnTheScreen();
    }
  });

  it("sin número no hay respuesta, aunque se elija unidad", async () => {
    const onAnswerChange = jest.fn();
    await renderWith(<NumericAnswer exercise={NUM} onAnswerChange={onAnswerChange} disabled={false} />);

    await fireEvent.press(screen.getByRole("radio", { name: "kA" }));
    expect(onAnswerChange).toHaveBeenLastCalledWith(null);
  });
});
