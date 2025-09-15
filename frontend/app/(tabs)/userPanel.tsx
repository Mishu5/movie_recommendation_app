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
import { useMemo, useState, useEffect } from "react";
import MediaCard from "../../components/mediaCard";
import { getPreferences, getMovieDetails } from "../../lib/functions";
import { handleChangePassword } from "../../lib/auth";

export default function UserPanel() {
  const { width } = useWindowDimensions();
  const numColumns = 3;
  const cardWidth = width / numColumns - 20;

  const [username] = useState("JohnDoe");
  const [newPassword, setNewPassword] = useState("");

  const [search, setSearch] = useState("");
  const [page, setPage] = useState(1);
  const pageSize = 6;

  const [ratedMovies, setRatedMovies] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  // fetching movie preferences
  useEffect(() => {
    const fetchUserPreferences = async () => {
      setLoading(true);
      const result = await getPreferences();
      if (!result.success) {
        console.warn("Error getting preferences:", result.message);
        setLoading(false);
        return;
      }

      const ids = result.preferences.map((p: any) => p.tconst);

      console.log("Fetched preferences:", ids);

      const details = await Promise.all(
        ids.map(async (id: string) => {
          const res = await getMovieDetails(id);
          if (!res.success || !res.movie) return null;
          const d = res.movie;

          let categories: string[] = [];
          if (Array.isArray(d.genres)) {
            categories = d.genres;
          } else if (typeof d.genres === "string") {
            categories = d.genres.split(",").map((c:any) => c.trim());
          }

          return {
            id: d.tconst,
            title: d.primaryTitle,
            posterUrl: d.poster,
            rating: d.averageRating ?? 0,
            numVotes: d.numVotes ?? 0,
            categories,
            userRating: d.user_rating ?? null,
          };
        })
      );

      setRatedMovies(details.filter(Boolean));
      setLoading(false);
    };

    fetchUserPreferences();
  }, []);

  const handleUpdatePassword = () => {
    if (!newPassword.trim()) {
      Alert.alert("Error", "Password cannot be empty");
      return;
    }
    setNewPassword("");
    Alert.alert("Success", "Password updated!");
  };

  // filtering and pagination
  const filtered = useMemo(() => {
    return ratedMovies.filter((m) =>
      m.title.toLowerCase().includes(search.toLowerCase())
    );
  }, [ratedMovies, search]);

  const processed = useMemo(
    () => filtered.slice(0, page * pageSize),
    [filtered, page]
  );

  const canLoadMore = processed.length < filtered.length;

return (
    <ScrollView
      style={{ flex: 1, backgroundColor: "#f8f8f8" }}
      contentContainerStyle={{ paddingBottom: 20 }}
      nestedScrollEnabled
    >
      {/* Settings */}
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
            setPage(1);
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

      {/* Rated media grid */}
      {loading ? (
        <Text style={{ textAlign: "center", marginTop: 20 }}>Loading...</Text>
      ) : (
        <FlatList
          data={processed}
          keyExtractor={(item) => item.id}
          numColumns={numColumns}
          scrollEnabled={false}
          nestedScrollEnabled
          contentContainerStyle={{ padding: 10 }}
          renderItem={({ item }) => (
            <View style={{ width: cardWidth, margin: 5 }}>
              <MediaCard {...item} onRate={() => {}} onDelete={() => {}} />
            </View>
          )}
        />
      )}

      {/* Load More */}
      {canLoadMore && !loading && (
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
