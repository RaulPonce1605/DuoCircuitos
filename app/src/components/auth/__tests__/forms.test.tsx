import { fireEvent, render, screen } from "@testing-library/react-native";

import { LoginForm } from "@/components/auth/login-form";
import { RegisterForm } from "@/components/auth/register-form";
import { AppProviders } from "@/components/app-providers";
import es from "@/i18n/es.json";
import { ApiError } from "@/services/api-client";

const mockSignIn = jest.fn();
const mockSignUp = jest.fn();

jest.mock("@/hooks/use-session", () => ({
  useSession: () => ({
    status: "signedOut",
    user: null,
    signIn: mockSignIn,
    signUp: mockSignUp,
    signOut: jest.fn(),
  }),
}));
jest.mock("expo-router", () => ({
  Link: ({ children }: { children: React.ReactNode }) => children,
}));

beforeEach(() => {
  mockSignIn.mockReset();
  mockSignUp.mockReset();
});

async function renderForm(form: React.ReactElement) {
  await render(<AppProviders>{form}</AppProviders>);
}

describe("LoginForm", () => {
  it("valida antes de llamar al backend", async () => {
    await renderForm(<LoginForm />);

    await fireEvent.press(screen.getByRole("button", { name: es.auth.login }));

    expect(screen.getByText(es.auth.invalidEmail)).toBeOnTheScreen();
    expect(screen.getByText(es.auth.missingPassword)).toBeOnTheScreen();
    expect(mockSignIn).not.toHaveBeenCalled();
  });

  it("envía correo y contraseña", async () => {
    mockSignIn.mockResolvedValue(undefined);
    await renderForm(<LoginForm />);

    await fireEvent.changeText(screen.getByLabelText(es.auth.email), "ana@example.com");
    await fireEvent.changeText(screen.getByLabelText(es.auth.password), "contraseña-segura");
    await fireEvent.press(screen.getByRole("button", { name: es.auth.login }));

    expect(mockSignIn).toHaveBeenCalledWith("ana@example.com", "contraseña-segura");
  });

  it("muestra el error del backend traducido, nunca el mensaje crudo", async () => {
    mockSignIn.mockRejectedValue(new ApiError("invalid_credentials", 401));
    await renderForm(<LoginForm />);

    await fireEvent.changeText(screen.getByLabelText(es.auth.email), "ana@example.com");
    await fireEvent.changeText(screen.getByLabelText(es.auth.password), "mal");
    await fireEvent.press(screen.getByRole("button", { name: es.auth.login }));

    expect(await screen.findByRole("alert")).toHaveTextContent(es.errors.invalid_credentials);
    expect(screen.queryByText("invalid_credentials")).toBeNull();
  });
});

describe("RegisterForm", () => {
  it("exige nombre, correo válido y contraseña de 8 o más", async () => {
    await renderForm(<RegisterForm />);

    await fireEvent.changeText(screen.getByLabelText(es.auth.email), "ana@");
    await fireEvent.changeText(screen.getByLabelText(es.auth.password), "corta");
    await fireEvent.press(screen.getByRole("button", { name: es.auth.register }));

    expect(screen.getByText(es.auth.missingName)).toBeOnTheScreen();
    expect(screen.getByText(es.auth.invalidEmail)).toBeOnTheScreen();
    expect(screen.getByText(es.auth.shortPassword)).toBeOnTheScreen();
    expect(mockSignUp).not.toHaveBeenCalled();
  });

  it("registra y muestra si el correo ya existe", async () => {
    mockSignUp.mockRejectedValue(new ApiError("email_taken", 409));
    await renderForm(<RegisterForm />);

    await fireEvent.changeText(screen.getByLabelText(es.auth.displayName), "Ana");
    await fireEvent.changeText(screen.getByLabelText(es.auth.email), "ana@example.com");
    await fireEvent.changeText(screen.getByLabelText(es.auth.password), "contraseña-segura");
    await fireEvent.press(screen.getByRole("button", { name: es.auth.register }));

    expect(mockSignUp).toHaveBeenCalledWith({
      email: "ana@example.com",
      password: "contraseña-segura",
      displayName: "Ana",
    });
    expect(await screen.findByRole("alert")).toHaveTextContent(es.errors.email_taken);
  });
});
