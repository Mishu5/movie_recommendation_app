import React, { createContext, useState, useEffect } from "react";
import AsyncStorage from "@react-native-async-storage/async-storage";

export const AuthContext = createContext({
  isLoggedIn: false,
  login: async (token: string) => {},
  logout: async () => {},
});

export const AuthProvider = ({ children }) => {
  const [isLoggedIn, setIsLoggedIn] = useState(false);

  // Check for JWT on mount
  useEffect(() => {
    const checkToken = async () => {
      const token = await AsyncStorage.getItem("jwt");
      setIsLoggedIn(!!token);
    };
    checkToken();
  }, []);

  const login = async (token: string) => {
    await AsyncStorage.setItem("jwt", token);
    setIsLoggedIn(true); // Update state so UI re-renders immediately
  };

  const logout = async () => {
    await AsyncStorage.removeItem("jwt");
    setIsLoggedIn(false); // Update state so UI re-renders immediately
  };

  return (
    <AuthContext.Provider value={{ isLoggedIn, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};
