import { io, Socket } from "socket.io-client";
import AsyncStorage from "@react-native-async-storage/async-storage";

const SOCKET_URL = "http://localhost:5000";

let socket: Socket | null = null;

// connection 

export async function connectSocket() {
    
    if( socket && socket.connected ) {
      return socket;
    }
    const jwt = await AsyncStorage.getItem("jwt");
    if (!jwt) throw new Error("Not logged in.");

    socket = io(SOCKET_URL, {
        transports: ["websocket"],
        auth: { jwt: jwt },
        reconnection: true,
    });

    socket.on("connect", () => {
        console.log("Connected to socket server"); 
    });

    socket.on("disconnect", (reason) => {
        console.log("Disconnected from socket server:", reason); 
    });

  return socket;
}

export function getSocket(): Socket | null {
    return socket;
}

// emiting events

// join a room
export async function joinRoomSocket(roomId: string) {
  const jwt = await AsyncStorage.getItem("jwt");
  if (!jwt) return;

  socket?.emit("join", { room_id: roomId, jwt });
}

// leave a room
export async function leaveRoomSocket(roomId: string) {
  const jwt = await AsyncStorage.getItem("jwt");
  if (!jwt) return;

  socket?.emit("leave", { room_id: roomId, jwt });
}

// start room (only creator)
export async function startRoomSocket(roomId: string) {
  const jwt = await AsyncStorage.getItem("jwt");
  if (!jwt) return;

  socket?.emit("message-start", { room_id: roomId, jwt });
}

// like a media
export async function likeMediaSocket(roomId: string, mediaId: string) {
  const jwt = await AsyncStorage.getItem("jwt");
  if (!jwt) return;

  socket?.emit("message-like", { room_id: roomId, jwt, media_id: mediaId });
}

// listening to events
export function setupSocketListeners(
  onMessageStarted: (data: any) => void,
  onError: (data: any) => void,
  onAllLiked: (data: any) => void
) {
  if (!socket) return;

  socket.on("message-started", onMessageStarted);
  socket.on("error", onError);
  socket.on("all-liked", onAllLiked);
}

// disconnecting

export function disconnectSocket() {
  if (socket) {
    socket.disconnect();
    socket = null;
    console.log("Socket disconnected");
  }
}