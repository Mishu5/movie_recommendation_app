import { Text, View, TextInput, Button, Pressable } from "react-native";
import { styles } from "../styles/styles";
import { useState, useContext } from "react";
import { handleLogin } from "../lib/auth";
import { buttonStyles } from "../styles/styles";
import AsyncStorage from "@react-native-async-storage/async-storage";
import { useRouter } from "expo-router";
import { AuthContext } from "../contexts/authContext";

export default function Login() {

  const[email, setEmail] = useState("");
  const[password, setPassword] = useState("");
  const { login } = useContext(AuthContext);

  const router = useRouter();

  const onSubmit = async () => {
    try{

      const result = await handleLogin(email, password);
      if (result.success) {
        console.log("Login successful");
      } else {
        console.error(result.message || "Login failed");
      }

      if (result.jwt) {
        await AsyncStorage.setItem("jwt", result.jwt);
        console.log("JWT stored successfully");
        router.replace("/"); // Navigate to the home screen after login
      }

    }catch(e){
      console.error("An error occurred during login: ", e);
    }
  };

  return (
    <View style={styles.container}>
      <Text>Log in</Text>
      <TextInput
        style={{ width: 200, height: 40, borderColor: "gray", borderWidth: 1, marginBottom: 12, paddingHorizontal: 8 }}
        placeholder="Email"
        value={email}
        onChangeText={setEmail}
        autoCapitalize="none"
        keyboardType="email-address"
      />
      <TextInput
        style={{ width: 200, height: 40, borderColor: "gray", borderWidth: 1, marginBottom: 12, paddingHorizontal: 8 }}
        placeholder="Password"
        value={password}
        onChangeText={setPassword}
        secureTextEntry
      />
      <Pressable style={buttonStyles.container} onPress={onSubmit}>
        <Text style={buttonStyles.text}>Log in</Text>
      </Pressable>
    </View>
  );
}