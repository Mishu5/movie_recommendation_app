import {
  View,
  FlatList,
  useWindowDimensions,
  Text,
  Pressable,
  TextInput,
} from "react-native";
import { useState, useEffect, useCallback } from "react";
import MediaCard from "../../components/mediaCard";
import { addPreference, removePreference } from "../../lib/functions";

export default function Index() {
  const { width } = useWindowDimensions();
  const numColumns = 4;
  const cardWidth = width / numColumns - 20;

  // --- State ---
  const [movies, setMovies] = useState<any[]>([]);
  const [allCategories, setAllCategories] = useState<string[]>([]);
  const [sortBy, setSortBy] = useState<"primaryTitle" | "averageRating">("primaryTitle");
  const [sortDir, setSortDir] = useState<"asc" | "desc">("asc");
  const [filterMinRating, setFilterMinRating] = useState<number>(0);
  const [selectedCategories, setSelectedCategories] = useState<string[]>([]);
  const [search, setSearch] = useState<string>("");
  const [page, setPage] = useState<number>(1);
  const [hasMore, setHasMore] = useState<boolean>(true);
  const pageSize = 8;

  // --- Fetch list of movie IDs + details ---
  const fetchMovies = useCallback(async () => {
    try {
      const query = new URLSearchParams({
        page: page.toString(),
        page_size: pageSize.toString(),
        sort_by: sortBy,
        sort_dir: sortDir,
        min_rating: filterMinRating.toString(),
        search,
      });
      selectedCategories.forEach((cat) => query.append("categories", cat));

      const res = await fetch(`http://localhost:5000/media?${query}`);
      const data = await res.json();

      const details = await Promise.all(
        data.ids.map(async (id: string) => {
          const r = await fetch(`http://localhost:5000/media/${id}`);
          const d = await r.json();

          let categories: string[] = [];
          if (Array.isArray(d.media.genres)) {
            categories = d.media.genres;
          } else if (typeof d.media.genres === "string") {
            categories = d.media.genres.split(",").map((c:any) => c.trim());
          }

          return {
            id: d.media.tconst,
            title: d.media.primaryTitle,
            posterUrl: d.media.poster,
            rating: d.media.averageRating ?? 0,
            numVotes: d.media.numVotes ?? 0,
            categories,
          };
        })
      );

      setMovies((prev) => (page === 1 ? details : [...prev, ...details]));
      setHasMore(data.has_more);

      // categories for filter chips
      if (page === 1) {
        const allCats = Array.from(new Set(details.flatMap((m) => m.categories)));
        setAllCategories(allCats);
      }
    } catch (err) {
      console.error(err);
    }
  }, [page, sortBy, sortDir, filterMinRating, selectedCategories, search]);

  useEffect(() => {
    setPage(1); // reset with change of filters
  }, [sortBy, sortDir, filterMinRating, selectedCategories, search]);

  useEffect(() => {
    fetchMovies();
  }, [fetchMovies, page]);

  // --- Handlers ---
  const toggleCategory = (cat: string) => {
    if (selectedCategories.includes(cat)) {
      setSelectedCategories(selectedCategories.filter((c) => c !== cat));
    } else {
      setSelectedCategories([...selectedCategories, cat]);
    }
  };

  const toggleAllCategories = () => {
    if (selectedCategories.length === allCategories.length) {
      setSelectedCategories([]);
    } else {
      setSelectedCategories(allCategories);
    }
  };

  const toggleSort = (field: "primaryTitle" | "averageRating") => {
    if (sortBy === field) {
      setSortDir(sortDir === "asc" ? "desc" : "asc");
    } else {
      setSortBy(field);
      setSortDir("asc");
    }
  };

  const handleRate = async (id: string, userRating: number) => {
    const result = await addPreference(id, userRating);
    if (!result.success) {
      console.error("Failed to add preference:", result.message);
    } else {
      console.log("Preference added:", result.message);
    }
    console.log(`User rated movie ${id} with ${userRating}`);
  };

  const handleDelete = async (id: string) => {
    const result = await removePreference(id);
    if (!result.success) {
      console.error("Failed to remove preference:", result.message);
    } else {
      console.log("Preference removed:", result.message);
    } 
    console.log(`User deleted rating for movie ${id}`);
  };

  return (
    <View style={{ flex: 1, backgroundColor: "#f8f8f8" }}>
      {/* Search */}
      <View
        style={{
          padding: 10,
          backgroundColor: "white",
          borderBottomWidth: 1,
          borderBottomColor: "#ddd",
        }}
      >
        <TextInput
          placeholder="Search movies..."
          value={search}
          onChangeText={setSearch}
          style={{
            backgroundColor: "#eee",
            padding: 8,
            borderRadius: 6,
          }}
        />
      </View>

      {/* Sort + Filter Row */}
      <View
        style={{
          flexDirection: "row",
          justifyContent: "space-around",
          padding: 10,
          backgroundColor: "white",
        }}
      >
        <Pressable onPress={() => toggleSort("primaryTitle")}>
          <Text style={{ color: sortBy === "primaryTitle" ? "#007AFF" : "black" }}>
            {sortBy === "primaryTitle" && sortDir === "asc" ? "Sort A–Z" : "Sort Z–A"}
          </Text>
        </Pressable>
        <Pressable onPress={() => toggleSort("averageRating")}>
          <Text style={{ color: sortBy === "averageRating" ? "#007AFF" : "black" }}>
            Rating:
            {sortBy === "averageRating" && sortDir === "desc"
              ? " Top → Least"
              : " Least → Top"}
          </Text>
        </Pressable>
        <Pressable
          onPress={() => setFilterMinRating((prev) => (prev === 8 ? 0 : 8))}
        >
          <Text style={{ color: filterMinRating === 8 ? "#007AFF" : "black" }}>
            {filterMinRating === 8 ? "All ratings" : "Filter ≥ 8"}
          </Text>
        </Pressable>
      </View>

      {/* Category Filter Row */}
      <View
        style={{
          flexDirection: "row",
          flexWrap: "wrap",
          padding: 10,
          backgroundColor: "white",
        }}
      >
        <Pressable
          onPress={toggleAllCategories}
          style={{
            paddingHorizontal: 12,
            paddingVertical: 8,
            margin: 4,
            borderRadius: 6,
            backgroundColor:
              selectedCategories.length === allCategories.length
                ? "#007AFF"
                : "#888",
          }}
        >
          <Text style={{ color: "white" }}>All</Text>
        </Pressable>
        {allCategories.map((cat) => (
          <Pressable
            key={cat}
            onPress={() => toggleCategory(cat)}
            style={{
              paddingHorizontal: 12,
              paddingVertical: 8,
              margin: 4,
              borderRadius: 6,
              backgroundColor: selectedCategories.includes(cat)
                ? "#007AFF"
                : "#888",
            }}
          >
            <Text style={{ color: "white" }}>{cat}</Text>
          </Pressable>
        ))}
      </View>

      {/* Movie Grid */}
      <FlatList
        data={movies}
        keyExtractor={(item) => item.id}
        numColumns={numColumns}
        columnWrapperStyle={{ justifyContent: "flex-start" }}
        contentContainerStyle={{ padding: 10 }}
        renderItem={({ item }) => (
          <View style={{ width: cardWidth, margin: 5 }}>
            <MediaCard
              key={item.id}
              {...item}
              onRate={handleRate}
              onDelete={handleDelete}
            />
          </View>
        )}
      />

      {/* Paging */}
      {hasMore && (
        <Pressable
          onPress={() => setPage((p) => p + 1)}
          style={{
            padding: 12,
            margin: 10,
            borderRadius: 8,
            backgroundColor: "#007AFF",
            alignItems: "center",
          }}
        >
          <Text style={{ color: "white", fontWeight: "bold" }}>Load More</Text>
        </Pressable>
      )}
    </View>
  );
}
