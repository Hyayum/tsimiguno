import { useState, useContext, createContext, useEffect } from "react";
import { CredentialResponse } from "@react-oauth/google";

type AuthContext = {
  credential: string;
  isAuthenticated: boolean;
  googleLogin: (res: CredentialResponse) => void;
  logout: () => void;
};

const defaultAuthContext: AuthContext = {
  credential: "",
  isAuthenticated: false,
  googleLogin: () => {},
  logout: () => {},
};

export const AuthContext = createContext(defaultAuthContext);

export const AuthProvider = ({ children }: { children: React.ReactNode }) => {
  const [credential, setCredential] = useState("");
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  const googleLogin = (response: CredentialResponse) => {
    if (response.credential) {
      setLogin(response.credential)
    }
  };

  const setLogin = (cred: string) => {
    setCredential(cred);
    setIsAuthenticated(true);
    localStorage.setItem("user", JSON.stringify({ credential: cred }));
  };

  const logout = () => {
    setCredential("");
    setIsAuthenticated(false);
    localStorage.removeItem("user");
  };

  useEffect(() => {
    const storedUser = localStorage.getItem("user");
    if (storedUser) {
      const cred = JSON.parse(storedUser).credential;
      if (cred) setLogin(cred);
    }
  }, []);

  return (
    <AuthContext value={{ credential, isAuthenticated, googleLogin, logout }}>
      {children}
    </AuthContext>
  );
};

export const useAuth = () => {
  return useContext(AuthContext);
};