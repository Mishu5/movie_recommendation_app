const API_URL = "http://localhost:5000/";

export async function handleLogin(email: string, password: string): Promise<{ success: boolean; message?: string, jwt?: string }> {
  if (!email || !password) {
    return { success: false, message: "Email and password are required.", jwt: ""};
  }
  return {success: true, message: "Login successful.", jwt: "jwt_token_here"};
  try {
    const response = await fetch(API_URL + "auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    });

    if (response.ok) {
      return { success: true };
    } else {
      const data = await response.json();
      return { success: false, message: data.message || "Login failed." };
    }
  } catch (error) {
    return { success: false, message: "Network error." };
  }
}

export async function handleRegister(email: string, password: string): Promise<{ success: boolean; message?: string, jwt?: string }> {
  if (!email || !password) {
    return { success: false, message: "Email and password are required.", jwt: ""};
  }
  return {success: true, message: "Login successful.", jwt: "jwt_token_here"};
  try {
    const response = await fetch(API_URL + "auth/register", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    });

    if (response.ok) {
      return { success: true };
    } else {
      const data = await response.json();
      return { success: false, message: data.message || "Register failed." };
    }
  } catch (error) {
    return { success: false, message: "Network error." };
  }
}