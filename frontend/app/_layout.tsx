import { Stack } from "expo-router";
import { buttonStyles } from "../styles/styles";
import { Text, Pressable } from "react-native";
import { useContext } from "react";
import { AuthContext, AuthProvider } from "../contexts/authContext";
import { useRouter } from "expo-router";

function LayoutWithAuth() {
  const router = useRouter();
  const { isLoggedIn, logout } = useContext(AuthContext);

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
            {!isLoggedIn ? (
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
            ) : (
              <Pressable style={buttonStyles.container} onPress={logout}>
                <Text style={buttonStyles.text}>Log out</Text>
              </Pressable>
            )}
          </>
        ),
      }}
    />
  );
}

export default function RootLayout() {
  return (
    <AuthProvider>
      <LayoutWithAuth />
    </AuthProvider>
  );
}
