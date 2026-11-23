import { fireEvent, render, screen } from "@testing-library/react-native";
import { Text } from "react-native";

import { Button, Card, Counter, ProgressBar } from "@/components/ui";

describe("Button", () => {
  it("muestra el texto y llama a onPress", async () => {
    const onPress = jest.fn();
    await render(<Button label="Comprobar" onPress={onPress} />);

    await fireEvent.press(screen.getByRole("button", { name: "Comprobar" }));
    expect(onPress).toHaveBeenCalledTimes(1);
    expect(screen.getByText("COMPROBAR")).toBeOnTheScreen();
  });

  it("no responde deshabilitado", async () => {
    const onPress = jest.fn();
    await render(<Button label="Comprobar" onPress={onPress} disabled />);

    const button = screen.getByRole("button", { name: "Comprobar" });
    await fireEvent.press(button);
    expect(onPress).not.toHaveBeenCalled();
    expect(button).toBeDisabled();
  });

  it("muestra que está ocupado mientras carga y no responde", async () => {
    const onPress = jest.fn();
    await render(<Button label="Comprobar" onPress={onPress} loading />);

    const button = screen.getByRole("button", { name: "Comprobar" });
    await fireEvent.press(button);
    expect(onPress).not.toHaveBeenCalled();
    expect(button).toBeBusy();
    expect(screen.queryByText("COMPROBAR")).toBeNull();
  });
});

describe("ProgressBar", () => {
  it.each([
    [0.4, 40],
    [0, 0],
    [1, 100],
    [1.7, 100],
    [-1, 0],
    [Number.NaN, 0],
  ])("progreso %p → %p %%", async (progress, percent) => {
    await render(<ProgressBar progress={progress} accessibilityLabel="Progreso de la lección" />);

    const bar = screen.getByRole("progressbar", { name: "Progreso de la lección" });
    expect(bar).toHaveAccessibilityValue({ min: 0, max: 100, now: percent });
    expect(screen.getByTestId("progress-fill")).toHaveStyle({ width: `${percent}%` });
  });
});

describe("Card", () => {
  it("sin onPress es solo un contenedor", async () => {
    await render(
      <Card>
        <Text>dentro</Text>
      </Card>,
    );
    expect(screen.getByText("dentro")).toBeOnTheScreen();
    expect(screen.queryByRole("button")).toBeNull();
  });

  it("con onPress es un botón accesible", async () => {
    const onPress = jest.fn();
    await render(
      <Card onPress={onPress} accessibilityLabel="Abrir lección">
        <Text>Ley de Ohm</Text>
      </Card>,
    );
    await fireEvent.press(screen.getByRole("button", { name: "Abrir lección" }));
    expect(onPress).toHaveBeenCalledTimes(1);
  });
});

describe("Counter", () => {
  it("muestra el valor y se anuncia con la frase completa", async () => {
    await render(
      <Counter icon="flame" value={3} color="streak" accessibilityLabel="Racha de 3 días" />,
    );
    expect(screen.getByText("3")).toBeOnTheScreen();
    expect(screen.getByLabelText("Racha de 3 días")).toBeOnTheScreen();
  });
});
