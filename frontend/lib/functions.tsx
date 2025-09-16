import AsyncStorage from "@react-native-async-storage/async-storage";

const API_URL = "http://localhost:5000/";

export async function addPreference(tconst: string, rating: number) {
  if (!tconst || rating == null) {
    return { success: false, message: "Movie ID and rating are required." };
  }
  try {
    const jwt = await AsyncStorage.getItem("jwt");
    if (!jwt) return { success: false, message: "Not logged in." };

    const response = await fetch(API_URL + "preferences/add", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ jwt, tconst, rating }),
    });

    const data = await response.json();
    if (response.ok) {
      return { success: true, message: data.message };
    } else {
      return { success: false, message: data.message };
    }
  } catch {
    return { success: false, message: "Network error." };
  }
}

export async function removePreference(tconst: string) {
  if (!tconst) {
    return { success: false, message: "Movie ID is required." };
  }
  try {
    const jwt = await AsyncStorage.getItem("jwt");
    if (!jwt) return { success: false, message: "Not logged in." }; 
    
    const repsonse = await fetch(API_URL + "preferences/delete", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ jwt, tconst }),
    });

    const data = await repsonse.json();
    if (repsonse.ok) {
      return { success: true, message: data.message };
    } else {
      return { success: false, message: data.message };
    }
  } catch {
    return { success: false, message: "Network error." };
  }
}

export async function getPreferences() {
  try {
    const jwt = await AsyncStorage.getItem("jwt");
    if (!jwt) return { success: false, message: "Not logged in." };

    const response = await fetch(API_URL + "preferences/get_all", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ jwt }),
    });

    const data = await response.json();
    if (response.ok) {
      return { success: true, preferences: data.preferences || [] };
    } else {
      return { success: false, message: data.message };
    }
  } catch {
    return { success: false, message: "Network error." };
  }
}

// ---------- ROOMS ----------

export async function createRoom() {
  try {
    const jwt = await AsyncStorage.getItem("jwt");
    if (!jwt) return { success: false, message: "Not logged in." };

    const response = await fetch(API_URL + "rooms/create", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ jwt }),
    });

    const data = await response.json();
    if (response.ok) {
      return { success: true, roomId: data.room_id };
    } else {
      return { success: false, message: data.message };
    }
  } catch {
    return { success: false, message: "Network error." };
  }
}

export async function joinRoom(roomId: string) {
  try {
    const jwt = await AsyncStorage.getItem("jwt");
    if (!jwt) return { success: false, message: "Not logged in." };

    const response = await fetch(API_URL + "rooms/join", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ jwt, room_id: roomId }),
    });

    const data = await response.json();
    if (response.ok) {
      return { success: true, message: data.message };
    } else {
      return { success: false, message: data.message };
    }
  } catch {
    return { success: false, message: "Network error." };
  }
}

// ---------- RECOMMENDATIONS ----------

export async function getRecommendations(roomId: string) {
  try {
    const jwt = await AsyncStorage.getItem("jwt");
    if (!jwt) return { success: false, message: "Not logged in." };

    const response = await fetch(API_URL + "rooms/recommendations", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ jwt, room_id: roomId }),
    });

    const data = await response.json();
    if (response.ok) {
      return { success: true, recommendations: data.recommended_media || [] };
    } else {
      return { success: false, message: data.message };
    }
  } catch {
    return { success: false, message: "Network error." };
  }
}

// ---------- Media ----------
export async function getMovieDetails(tconst: string) {

  const jwt = await AsyncStorage.getItem("jwt");
  if (!tconst) {
    return { success: false, message: "Movie ID is required." };
  }
  try {
    const response = await fetch(API_URL + `media/${tconst}`,
      {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ jwt }),
    }
    );
    const data = await response.json();
    if (response.ok) {
      return { success: true, movie: data.media };
    } else {
      return { success: false, message: data.message };
    }
  } catch {
    return { success: false, message: "Network error." };
  }
}

// ---------- User ----------
export async function getUserDetails() {
  try {
    const jwt = await AsyncStorage.getItem("jwt");
    if (!jwt) return { success: false, message: "Not logged in." }; 
    const response = await fetch(API_URL + "user_data", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ jwt }),
    });
    const data = await response.json();
    if (response.ok) {
      return { success: true, userData: data };
    } else {
      return { success: false, message: data.message };
    }
  } catch {
    return { success: false, message: "Network error." };
  }
}