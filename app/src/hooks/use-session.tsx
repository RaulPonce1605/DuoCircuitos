import { useQueryClient } from "@tanstack/react-query";
import { createContext, type ReactNode, useContext, useEffect, useMemo, useState } from "react";

import { authService, type RegisterInput, type User } from "@/services/auth-service";
import { remindersService } from "@/services/reminders";

type SessionStatus = "loading" | "signedOut" | "signedIn";

type SessionValue = {
  status: SessionStatus;
  user: User | null;
  signIn: (email: string, password: string) => Promise<void>;
  signUp: (input: RegisterInput) => Promise<void>;
  signOut: () => Promise<void>;
};

const SessionContext = createContext<SessionValue | null>(null);

export function SessionProvider({ children }: { children: ReactNode }) {
  const queryClient = useQueryClient();
  const [status, setStatus] = useState<SessionStatus>("loading");
  const [user, setUser] = useState<User | null>(null);

  useEffect(() => {
    const unsubscribe = authService.subscribe((next) => {
      setUser(next);
      setStatus(next ? "signedIn" : "signedOut");
      if (!next) {
        queryClient.clear(); // nada de los datos del usuario anterior queda en caché
        void remindersService.clear(); // ni sus avisos programados
      }
    });
    authService.restore().then(
      (restored) => {
        if (!restored) {
          setStatus("signedOut");
        }
      },
      () => setStatus("signedOut"), // sin red al abrir: se pide iniciar sesión
    );
    return unsubscribe;
  }, [queryClient]);

  const value = useMemo<SessionValue>(
    () => ({
      status,
      user,
      signIn: async (email, password) => {
        await authService.login(email, password);
      },
      signUp: async (input) => {
        await authService.register(input);
      },
      signOut: () => authService.logout(),
    }),
    [status, user],
  );

  return <SessionContext.Provider value={value}>{children}</SessionContext.Provider>;
}

export function useSession(): SessionValue {
  const value = useContext(SessionContext);
  if (!value) {
    throw new Error("useSession debe usarse dentro de <SessionProvider>");
  }
  return value;
}
