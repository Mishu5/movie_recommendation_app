import { useEffect, useState } from 'react';
import { View, Text, Button } from 'react-native';
import io from 'socket.io-client';

const socket = io('http://localhost:5000');

export default function RoomScreen() {
  const [room, setRoom] = useState<string | null>(null);

  useEffect(() => {
    socket.on('room_update', (data: { room: string }) => {
      setRoom(data.room);
    });

    return () => {
      socket.off('room_update');
    };
  }, []);

  function joinRoom() {
    socket.emit('join_room', { userId: 123 });
  }

  return (
    <View>
      <Text>Your room: {room || 'None'}</Text>
      <Button title="Join room" onPress={joinRoom} />
    </View>
  );
}
