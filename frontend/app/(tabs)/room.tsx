import { Text, View, Image, Button, TextInput } from "react-native";
import { useEffect, useState, useRef } from "react";
import AsyncStorage from "@react-native-async-storage/async-storage";
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

export default function Room() {
  const [roomCode, setRoomCode] = useState("");
  const [roomId, setRoomId] = useState("");
  const [isCreator, setIsCreator] = useState(false);
  const [recommendations, setRecommendations] = useState<string[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [currentMovie, setCurrentMovie] = useState<any>(null);
  const [roomActive, setRoomActive] = useState(false);

  const roomIdRef = useRef(roomId);
  useEffect(() => {
    roomIdRef.current = roomId;
  }, [roomId]);

  // Restore room data on mount
  useEffect(() => {
    const restoreRoomData = async () => {
      try {
        const savedRoomId = await AsyncStorage.getItem("roomId");
        const savedRecommendations = await AsyncStorage.getItem("recommendations");
        const savedIndex = await AsyncStorage.getItem("currentIndex");
        const savedIsCreator = await AsyncStorage.getItem("isCreator");
        const savedRoomActive = await AsyncStorage.getItem("roomActive");

        if (savedRoomId) setRoomId(savedRoomId);
        if (savedRecommendations) setRecommendations(JSON.parse(savedRecommendations));
        if (savedIndex) setCurrentIndex(parseInt(savedIndex));
        if (savedIsCreator) setIsCreator(savedIsCreator === "true");
        if (savedRoomActive) setRoomActive(savedRoomActive === "true");
      } catch (e) {
        console.error("Error restoring room data:", e);
      }
    };
    restoreRoomData();
  }, []);

  // Save room data whenever state changes
  useEffect(() => {
    const saveRoomData = async () => {
      try {
        await AsyncStorage.setItem("roomId", roomIdRef.current);
        await AsyncStorage.setItem("recommendations", JSON.stringify(recommendations));
        await AsyncStorage.setItem("currentIndex", currentIndex.toString());
        await AsyncStorage.setItem("isCreator", isCreator.toString());
        await AsyncStorage.setItem("roomActive", roomActive.toString());
      } catch (e) {
        console.error("Error saving room data:", e);
      }
    };
    saveRoomData();
  }, [roomId, recommendations, currentIndex, isCreator, roomActive]);

  // Socket connection and listeners
  useEffect(() => {
    connectSocket()
      .then(() => {
        console.log("Socket connected in Room component");
        setupSocketListeners(
          (data) => {
            console.log("Room started:", data);
            setRoomActive(true);
            handleStartRoom(roomIdRef.current);
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
      if (roomIdRef.current) leaveRoomSocket(roomIdRef.current);
      disconnectSocket();
    };
  }, []);

  // Fetch movie details when currentIndex or recommendations change
  useEffect(() => {
    if (recommendations.length > 0 && currentIndex < recommendations.length) {
      fetchMovie(recommendations[currentIndex]);
    } else {
      setCurrentMovie(null);
    }
  }, [recommendations, currentIndex]);

  const fetchMovie = async (tconst: string) => {
    try {
      const res = await getMovieDetails(tconst);
      setCurrentMovie(res.movie);
      console.log("Fetched movie details:", res.movie);
    } catch (error) {
      console.error("Error fetching movie data: ", error);
    }
  };

  const showNextMovie = () => setCurrentIndex((prev) => prev + 1);

  const handleCreateRoom = async () => {
    try {
      const res = await createRoom();
      if (res.success && res.roomId) {
        setIsCreator(true);
        setRoomId(res.roomId);
        joinRoomSocket(res.roomId);
        console.log("Room created with ID:", res.roomId);
      } else console.error("Failed to create room:", res.message);
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
      } else console.error("Failed to join room:", res.message);
    } catch (e) {
      console.error("Failed to join room:", e);
    }
  };

  const handleRoomStartCommand = () => {
    if (roomIdRef.current) startRoomSocket(roomIdRef.current);
    else console.error("No room ID available to start the room.");
  };

  const handleStartRoom = async (currentRoomId: string) => {
    console.log("Handling room start for room ID:", currentRoomId);
    if (currentRoomId) {
      const res = await getRecommendations(currentRoomId);
      console.log("Recommendations fetched:", res);
      if (res.success) {
        setRecommendations(res.recommendations);
        setCurrentIndex(0);
        fetchMovie(res.recommendations[0]);  
      } else console.error("Failed to get recommendations:", res.message);
    }
  };

  const handleLike = () => {
    if (roomIdRef.current && currentMovie) {
      likeMediaSocket(roomIdRef.current, currentMovie.tconst);
      showNextMovie();
    }
  };

  const handleDislike = () => showNextMovie();

  // --- Leave room and clear all state ---
  const handleLeaveRoom = async () => {
    if (roomIdRef.current) leaveRoomSocket(roomIdRef.current);

    // Clear state
    setRoomId("");
    setIsCreator(false);
    setRecommendations([]);
    setCurrentIndex(0);
    setRoomActive(false);
    setCurrentMovie(null);

    // Remove from AsyncStorage
    try {
      await AsyncStorage.multiRemove([
        "roomId",
        "isCreator",
        "recommendations",
        "currentIndex",
        "roomActive",
      ]);
      console.log("Room data cleared from AsyncStorage");
    } catch (e) {
      console.error("Error clearing room data:", e);
    }
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
          {isCreator && !roomActive && (
            <Button title="Start Room" onPress={handleRoomStartCommand} />
          )}
          <Button title="Leave Room" onPress={handleLeaveRoom} color="red" />

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
