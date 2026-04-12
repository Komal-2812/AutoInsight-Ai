import { createContext, useContext, useState, ReactNode } from "react";

interface User {
  id: string;
  email?: string;
  full_name?: string; // ✅ ADD THIS
}

interface AuthContextType {
  user: User | null;
  loading: boolean;
  signIn: (email: string, password: string) => Promise<any>;
  signUp: (email: string, password: string, fullName: string) => Promise<any>;
  signOut: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>({ id: "demo-user" });
  const [loading, setLoading] = useState(false);

  const signIn = async (email: string, password: string) => {
    // OPTIONAL: connect to FastAPI later
    setUser({ id: "demo-user", email });
    return { error: null };
  };

  const signUp = async (email: string, password: string, fullName: string) => {
    setUser({ id: "demo-user", email });
    return { error: null };
  };

  const signOut = async () => {
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, loading, signIn, signUp, signOut }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}