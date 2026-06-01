import { createContext, useContext, useEffect, useState } from "react";
import { tokenStore } from "../api/client";
import { authApi } from "../api/resources";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function bootstrap() {
      if (tokenStore.access) {
        try {
          const { data } = await authApi.me();
          setUser(data);
        } catch {
          tokenStore.clear();
        }
      }
      setLoading(false);
    }
    bootstrap();
  }, []);

  async function login(credentials) {
    const { data } = await authApi.login(credentials);
    tokenStore.set(data);
    const me = await authApi.me();
    setUser(me.data);
    return me.data;
  }

  async function register(payload) {
    await authApi.register(payload);
    return login({ email: payload.email, password: payload.password });
  }

  function logout() {
    tokenStore.clear();
    setUser(null);
  }

  return (
    <AuthContext.Provider
      value={{ user, loading, login, register, logout, isAdmin: user?.role === "admin" }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
