"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";
import { AuthService, type UserPublic } from "../../src/generated/api";
import { setAccessToken } from "../../lib/api/runtime";
import { usePathname } from "next/navigation";

type AuthState = {
  user?: UserPublic;
  ready: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
};
const AuthContext = createContext<AuthState | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const pathname = usePathname();
  const [user, setUser] = useState<UserPublic | undefined>(undefined);
  const [ready, setReady] = useState(false);
  const accept = useCallback((token: string, nextUser: UserPublic) => {
    setAccessToken(token);
    setUser(nextUser);
  }, []);
  useEffect(() => {
    const protectedRoute =
      pathname.startsWith("/dashboard") || pathname === "/settings";
    if (!protectedRoute || user) {
      setReady(true);
      return;
    }
    AuthService.refreshRouteApiV1AuthRefreshPost({})
      .then((response) =>
        accept(response.data.access_token, response.data.user),
      )
      .catch(() => setAccessToken())
      .finally(() => setReady(true));
  }, [accept, pathname, user]);
  const login = useCallback(
    async (email: string, password: string) => {
      const response = await AuthService.loginRouteApiV1AuthLoginPost({
        requestBody: { email, password },
      });
      accept(response.data.access_token, response.data.user);
    },
    [accept],
  );
  const logout = useCallback(() => {
    setAccessToken();
    setUser(undefined);
  }, []);
  const value = useMemo(
    () => ({ user, ready, login, logout }),
    [user, ready, login, logout],
  );
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
export function useAuth() {
  const value = useContext(AuthContext);
  if (!value) throw new Error("useAuth must be inside AuthProvider");
  return value;
}
