import { Text, View, Image, Button, Pressable,TextInput } from "react-native";
import { styles } from "../../styles/styles";
import { useEffect, useState } from "react";
import axios from "axios";
import {
  connectSocket,
  disconnectSocket,
  setupSocketListeners,
  joinRoomSocket,
  leaveRoomSocket,
  startRoomSocket,
  likeMediaSocket,
} from "../../lib/sockets";

const API_URL = "http://localhost:5000";

export default function Room() {

  const [roomCode, setRoomCode] = useState("");
  const [roomId, setRoomId] = useState("");
  const [isCreator, setIsCreator] = useState(false);
  const [recommendations, setRecommendations] = useState<string[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [currentMovie, setCurrentMovie] = useState<any>(null);

  // Connection

  useEffect(() => {

    connectSocket().then(() => {
      console.log("Socket connected in Room component");
      setupSocketListeners(
        (data) => { console.log("Room started:", data); },
        (error) => { console.error("Socket error:", error); },
        (data) => { console.log("Media all liked:", data); }  
      );
    }).catch((error) => {
      console.error("Socket connection error in Room component:", error);
    });  

    return () => {
      if (roomId) {leaveRoomSocket(roomId);}
      disconnectSocket();
    }
  }, []);

  // Fetch media info when currentMovie changes

  useEffect(() => {
    if (recommendations.length > 0 && currentIndex < recommendations.length) {
      const tconst = recommendations[currentIndex];
      fetchMovie(tconst);
    } else {
      setCurrentMovie(null);
    }
  }, [recommendations, currentIndex]);

  const fetchMovie = async (tconst: string) => {
    try{
      const res = await axios.get(`${API_URL}movie/${tconst}`);
      setCurrentMovie(res.data);
    } catch (error) {
      console.error("Error fetching movie data: ", error);
    }
  };

  const showNextMovie = () => {
    setCurrentIndex((prevIndex) => prevIndex + 1);
  };

  const handleCreateRoom = async () => {
    try {
      const res = await axios.post(`${API_URL}/rooms/create`);
      setRoomId(res.data.room_id);
      setIsCreator(true);
      joinRoomSocket(res.data.room_id);
    } catch (e) {
      console.error("Failed to create room:", e);
    }
  };

  const handleJoinRoom = async () => {
    try {
      const res = await axios.post(`${API_URL}/rooms/join`, { room_id: roomCode });
      setRoomId(res.data.room_id);
      setIsCreator(false);
      joinRoomSocket(res.data.room_id);
    } catch (e) {
      console.error("Failed to join room:", e);
    }
  };

  const handleStartRoom = () => {
    if (roomId) startRoomSocket(roomId);
  };

  const handleLike = () => {
    if (roomId && currentMovie) likeMediaSocket(roomId, currentMovie.tconst);
  };

  const handleDislike = () => {
    // just skip locally (server only tracks likes)
    showNextMovie();
  };

  return (
    <View style={{ flex: 1, padding: 20 }}>
      {!roomId ? (
        <>
          <Button title="Create Room" onPress={handleCreateRoom} />
          <TextInput
            placeholder="Enter Room Code"
            value={roomCode}
            onChangeText={setRoomCode}
            style={{
              borderWidth: 1,
              borderColor: "#ccc",
              padding: 10,
              marginVertical: 10,
            }}
          />
          <Button title="Join Room" onPress={handleJoinRoom} />
        </>
      ) : (
        <>
          <Text>Room: {roomId}</Text>
          {isCreator && <Button title="Start Room" onPress={handleStartRoom} />}

          {currentMovie ? (
            <View style={{ marginTop: 20, alignItems: "center" }}>
              <Text style={{ fontSize: 20, fontWeight: "bold" }}>
                {currentMovie.primaryTitle}
              </Text>
              {currentMovie.poster && (
                <Image
                  source={{ uri: currentMovie.poster }}
                  style={{ width: 200, height: 300, marginVertical: 10 }}
                  resizeMode="cover"
                />
              )}
              <Text>{currentMovie.plot || "No description available"}</Text>
              <View style={{ flexDirection: "row", marginTop: 20 }}>
                <Button title="Dislike" onPress={handleDislike} />
                <View style={{ width: 20 }} />
                <Button title="Like" onPress={handleLike} />
              </View>
            </View>
          ) : (
            <Text style={{ marginTop: 20 }}>No more movies</Text>
          )}
        </>
      )}
    </View>
  );
}
