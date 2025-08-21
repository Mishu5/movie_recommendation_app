import { StyleSheet } from "react-native";

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
    backgroundColor: "rgba(255, 255, 255, 1)",
  }
});

const buttonStyles = StyleSheet.create({
  container: {
    marginRight: 16,
    paddingVertical: 6,
    paddingHorizontal: 12,
    borderRadius: 4,
    backgroundColor: "#ff3c00",
    alignItems: "center",
    justifyContent: "center",
  },
  text: {
    color: "#fff",             
    fontSize: 16,
    fontWeight: "bold",
  },
});

export { styles, buttonStyles };
