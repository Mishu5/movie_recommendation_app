import { Stack, Tabs, useRouter } from "expo-router";
import { buttonStyles } from "../styles/styles";
import { Text, Pressable } from "react-native";

export default function RootLayout() {

  const router = useRouter();

  return (
  <Stack
    screenOptions={{
      headerTitle: () => (
        <Text
          style={{
            textDecorationLine: "none",
            color: "#007AFF",
            fontWeight: "bold",
            fontSize: 20,
          }}
        >
          Movie Recommendation Site
        </Text>
      ),
      headerRight: () => (
        <>
          <Pressable
            style={buttonStyles.container}
            onPress={() => router.push("/login")}
          >
            <Text style={buttonStyles.text}>Log in</Text>
          </Pressable>

          <Pressable
            style={buttonStyles.container}
            onPress={() => router.push("/register")}
          >
            <Text style={buttonStyles.text}>Register</Text>
          </Pressable>
        </>
      ),
    }}
  >
  </Stack>
  );
}
