import { View, Text, Button } from 'react-native';

export default function UserScreen() {
  async function handleLogout() {

  }

  return (
    <View>
      <Text>Welcome to user panel!</Text>
      <Button title="Log out" onPress={handleLogout} />
    </View>
  );
}
