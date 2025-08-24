import {
  View,
  Text,
  Pressable,
  TextInput,
  FlatList,
  useWindowDimensions,
  Alert,
  ScrollView,
} from "react-native";
import { useMemo, useState } from "react";
import MediaCard from "../../components/mediaCard";

export default function UserPanel() {
  const { width } = useWindowDimensions();
  const numColumns = 3;
  const cardWidth = width / numColumns - 20;

  // --- Mock user data ---
  const [username] = useState("JohnDoe");

  // --- Password change ---
  const [newPassword, setNewPassword] = useState("");

  // --- Search + paging (same pattern as Index) ---
  const [search, setSearch] = useState("");
  const [page, setPage] = useState(1);
  const pageSize = 6;

  // --- Mock rated media ---
  const ratedMovies = [
    { id: "1",  title: "Inception",           posterUrl: "https://m.media-amazon.com/images/I/51xJ9O4ZQdL._AC_.jpg", rating: 9,  categories: ["Sci-Fi", "Thriller"] },
    { id: "2",  title: "The Dark Knight",     posterUrl: "https://m.media-amazon.com/images/I/51EbJjlY7zL._AC_.jpg", rating: 10, categories: ["Action", "Drama"] },
    { id: "3",  title: "Interstellar",        posterUrl: "https://m.media-amazon.com/images/I/71n58u3tC7L._AC_SY679_.jpg", rating: 8,  categories: ["Sci-Fi", "Drama"] },
    { id: "4",  title: "Avatar",              posterUrl: "https://m.media-amazon.com/images/I/61OUGpUfAyL._AC_SY679_.jpg", rating: 7,  categories: ["Sci-Fi", "Adventure"] },
    { id: "5",  title: "The Matrix",          posterUrl: "https://m.media-amazon.com/images/I/51EG732BV3L.jpg", rating: 9,  categories: ["Sci-Fi", "Action"] },
    { id: "6",  title: "Titanic",             posterUrl: "https://m.media-amazon.com/images/I/71n58u3tC7L._AC_SY679_.jpg", rating: 8,  categories: ["Drama", "Romance"] },
    { id: "7",  title: "Joker",               posterUrl: "https://m.media-amazon.com/images/I/51EbJjlY7zL._AC_.jpg", rating: 8,  categories: ["Drama", "Thriller"] },
    { id: "8",  title: "Forrest Gump",        posterUrl: "https://m.media-amazon.com/images/I/61+z4vtpWML._AC_SY741_.jpg", rating: 9,  categories: ["Drama", "Romance"] },
    { id: "9",  title: "Pulp Fiction",        posterUrl: "https://m.media-amazon.com/images/I/71c05lTE03L._AC_SY679_.jpg", rating: 9,  categories: ["Crime", "Drama"] },
    { id: "10", title: "The Lion King",       posterUrl: "https://m.media-amazon.com/images/I/81s6DUyQCZL._AC_SY679_.jpg", rating: 8,  categories: ["Animation", "Drama"] },
  ];

  const handleUpdatePassword = () => {
    if (!newPassword.trim()) {
      Alert.alert("Error", "Password cannot be empty");
      return;
    }
    setNewPassword("");
    Alert.alert("Success", "Password updated!");
  };

  // --- Filtering + "Load More" pagination (identical approach) ---
  const filtered = useMemo(
    () =>
      ratedMovies.filter((m) =>
        m.title.toLowerCase().includes(search.toLowerCase())
      ),
    [ratedMovies, search]
  );

  const processed = useMemo(
    () => filtered.slice(0, page * pageSize),
    [filtered, page]
  );

  const canLoadMore = processed.length < filtered.length;

  return (
    <ScrollView style={{ flex: 1, backgroundColor: "#f8f8f8" }}>
      {/* Settings card */}
      <View
        style={{
          padding: 15,
          backgroundColor: "white",
          margin: 10,
          borderRadius: 10,
        }}
      >
        <Text style={{ fontSize: 16, fontWeight: "bold", marginBottom: 8 }}>
          Account Settings
        </Text>

        <Text style={{ marginBottom: 12 }}>Username: {username}</Text>

        <TextInput
          placeholder="Enter new password"
          value={newPassword}
          onChangeText={setNewPassword}
          secureTextEntry
          style={{
            borderWidth: 1,
            borderColor: "#ccc",
            padding: 8,
            marginBottom: 8,
            borderRadius: 6,
          }}
        />
        <Pressable
          onPress={handleUpdatePassword}
          style={{
            backgroundColor: "#007AFF",
            padding: 10,
            borderRadius: 6,
            alignItems: "center",
          }}
        >
          <Text style={{ color: "white" }}>Change Password</Text>
        </Pressable>
      </View>

      {/* Search */}
      <View style={{ marginHorizontal: 10, marginBottom: 10 }}>
        <TextInput
          placeholder="Search by name..."
          value={search}
          onChangeText={(t) => {
            setSearch(t);
            setPage(1); // reset paging on new search
          }}
          style={{
            borderWidth: 1,
            borderColor: "#ccc",
            padding: 8,
            borderRadius: 6,
            backgroundColor: "white",
          }}
        />
      </View>

      {/* Banner */}
      <View
        style={{
          backgroundColor: "#007AFF",
          paddingVertical: 15,
          alignItems: "center",
          marginHorizontal: 10,
          borderRadius: 10,
        }}
      >
        <Text style={{ color: "white", fontSize: 20, fontWeight: "bold" }}>
          My rated media
        </Text>
      </View>

      {/* Rated media grid (non-scrolling FlatList; ScrollView handles the scroll) */}
      <FlatList
        data={processed}
        keyExtractor={(item) => item.id}
        numColumns={numColumns}
        scrollEnabled={false}
        contentContainerStyle={{ padding: 10 }}
        renderItem={({ item }) => (
          <View style={{ width: cardWidth, margin: 5 }}>
            <MediaCard
              key={item.id}
              {...item}
              onRate={() => {}}
              onDelete={() => {}}
            />
          </View>
        )}
      />

      {/* Load More (same logic as Index) */}
      {canLoadMore && (
        <Pressable
          onPress={() => setPage((p) => p + 1)}
          style={{
            padding: 12,
            marginHorizontal: 10,
            marginBottom: 20,
            borderRadius: 8,
            backgroundColor: "#007AFF",
            alignItems: "center",
          }}
        >
          <Text style={{ color: "white", fontWeight: "bold" }}>Load More</Text>
        </Pressable>
      )}
    </ScrollView>
  );
}
