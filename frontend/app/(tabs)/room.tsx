import { Text, View, Image, Button, TextInput } from "react-native";
import { useEffect, useState, useRef } from "react";
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
import { createRoom, joinRoom, getRecommendations, getMovieDetails } from "../../lib/functions";

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
    connectSocket()
      .then(() => {
        console.log("Socket connected in Room component");
        setupSocketListeners(
          (data) => {
            console.log("Room started:", data);
            // Fetch recommendations when room starts
            handleStartRoom();
          },
          (error) => {
            console.error("Socket error:", error);
          },
          (data) => {
            console.log("Media all liked:", data);
          }
        );
      })
      .catch((error) => {
        console.error("Socket connection error in Room component:", error);
      });

    return () => {
      if (roomId) {
        leaveRoomSocket(roomId);
      }
      disconnectSocket();
    };
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
    try {
      const res = await getMovieDetails(tconst);
      setCurrentMovie(res.movie);
    } catch (error) {
      console.error("Error fetching movie data: ", error);
    }
  };

  const showNextMovie = () => {
    setCurrentIndex((prevIndex) => prevIndex + 1);
  };

  const handleCreateRoom = async () => {
    try {
      const res = await createRoom();
      if (res.success && res.roomId) {
        setIsCreator(true);
        setRoomId(res.roomId);
        joinRoomSocket(res.roomId);
        console.log("Room created with ID:", res.roomId);
      } else {
        console.error("Failed to create room:", res.message);
      }
    } catch (e) {
      console.error("Failed to create room:", e);
    }
  };

  const handleJoinRoom = async () => {
    try {
      const res = await joinRoom(roomCode);
      if (res.success) {
        setRoomId(roomCode);
        setIsCreator(false);
        joinRoomSocket(roomCode);
      } else {
        console.error("Failed to join room:", res.message);
      }
    } catch (e) {
      console.error("Failed to join room:", e);
    }
  };

  const handleRoomStartCommand = async () => {
    if (roomId) {
      startRoomSocket(roomId);
    } else {
      console.error("No room ID available to start the room.");
    }
  };

  const handleStartRoom = async () => {
    console.log("Fetching recommendations for room:", roomId);
    if (roomId) {
      const res = await getRecommendations(roomId);
      console.log("Recommendations fetched:", res);
      if (res.success) {
        setRecommendations(res.recommendations);
        setCurrentIndex(0);
      } else {
        console.error("Failed to get recommendations:", res.message);
      }
    } else {
      console.error("No room ID available to fetch recommendations.");
    }
  };

  const handleLike = () => {
    if (roomId && currentMovie) {
      likeMediaSocket(roomId, currentMovie.tconst);
      showNextMovie();
    }
  };

  const handleDislike = () => {
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
          {isCreator && <Button title="Start Room" onPress={handleRoomStartCommand} />}

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
