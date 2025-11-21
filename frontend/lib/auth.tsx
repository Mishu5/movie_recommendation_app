import AsyncStorage from "@react-native-async-storage/async-storage";
const API_URL = "http://192.168.0.105:5000/";

export async function handleLogin(
  email: string,
  password: string
): Promise<{ success: boolean; message?: string; jwt?: string }> {
  if (!email || !password) {
    return { success: false, message: "Email and password are required.", jwt: "" };
  }

  try {
    const response = await fetch(API_URL + "auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    });

    const data = await response.json();

    if (response.ok) {
      return { success: true, jwt: data.jwt, message: "Login successful." };
    } else {
      return { success: false, message: data.message || "Login failed." };
    }
  } catch (error) {
    return { success: false, message: "Network error." };
  }
}

export async function handleRegister(
  email: string,
  password: string
): Promise<{ success: boolean; message?: string; jwt?: string }> {
  if (!email || !password) {
    return { success: false, message: "Email and password are required.", jwt: "" };
  }

  try {
    const response = await fetch(API_URL + "auth/register", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    });

    const data = await response.json();

    if (response.ok) {
      return { success: true, jwt: data.jwt, message: "Register successful." };
    } else {
      return { success: false, message: data.message || "Register failed." };
    }
  } catch (error) {
    return { success: false, message: "Network error." };
  }
}

export async function handleChangePassword(
  newPassword: string
): Promise<{ success: boolean; message?: string }> {
  if (!newPassword) {
    return { success: false, message: "New password is required." };
  }
  
  try {
    const jwt = await AsyncStorage.getItem("jwt");
    if (!jwt) return { success: false, message: "Not logged in." };
    const response = await fetch(API_URL + "auth/change_password", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ jwt, new_password: newPassword }),
    } );  
  
    const data = await response.json();
    console.log(data);
    if (response.ok) {
      return { success: true, message: data.message };
    } else {
      return { success: false, message: data.message };
    }
  } catch {
    return { success: false, message: "Network error." };
  }
}