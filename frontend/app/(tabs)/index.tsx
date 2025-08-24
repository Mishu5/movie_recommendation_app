import {
  View,
  FlatList,
  useWindowDimensions,
  Text,
  Pressable,
  TextInput,
} from "react-native";
import { useState, useMemo } from "react";
import MediaCard from "../../components/mediaCard";

export default function Index() {
  // --- Mock backend-like data ---
  const movies = [
    {
      id: "1",
      title: "Inception",
      posterUrl: "https://m.media-amazon.com/images/I/51xJ9O4ZQdL._AC_.jpg",
      rating: 8.7,
      categories: ["Sci-Fi", "Thriller"],
    },
    {
      id: "2",
      title: "The Matrix",
      posterUrl: "https://m.media-amazon.com/images/I/51EG732BV3L.jpg",
      rating: 8.6,
      categories: ["Sci-Fi", "Action"],
    },
    {
      id: "3",
      title: "Interstellar",
      posterUrl:
        "https://m.media-amazon.com/images/I/71n58u3tC7L._AC_SY679_.jpg",
      rating: 8.5,
      categories: ["Sci-Fi", "Drama"],
    },
    {
      id: "4",
      title: "Avatar",
      posterUrl:
        "https://m.media-amazon.com/images/I/61OUGpUfAyL._AC_SY679_.jpg",
      rating: 7.8,
      categories: ["Sci-Fi", "Adventure"],
    },
    {
      id: "5",
      title: "The Dark Knight",
      posterUrl: "https://m.media-amazon.com/images/I/51EbJjlY7zL._AC_.jpg",
      rating: 9.0,
      categories: ["Action", "Drama"],
    },
    {
      id: "6",
      title: "Fight Club",
      posterUrl: "https://m.media-amazon.com/images/I/51v5ZpFyaFL._AC_.jpg",
      rating: 8.8,
      categories: ["Drama"],
    },
    {
      id: "7",
      title: "Pulp Fiction",
      posterUrl:
        "https://m.media-amazon.com/images/I/71c05lTE03L._AC_SY679_.jpg",
      rating: 8.9,
      categories: ["Crime", "Drama"],
    },
    {
      id: "8",
      title: "Avengers: Endgame",
      posterUrl:
        "https://m.media-amazon.com/images/I/81ExhpBEbHL._AC_SY679_.jpg",
      rating: 8.4,
      categories: ["Action", "Adventure", "Sci-Fi"],
    },
    {
      id: "9",
      title: "The Lion King",
      posterUrl:
        "https://m.media-amazon.com/images/I/81s6DUyQCZL._AC_SY679_.jpg",
      rating: 8.5,
      categories: ["Animation", "Drama"],
    },
    {
      id: "10",
      title: "Forrest Gump",
      posterUrl:
        "https://m.media-amazon.com/images/I/61+z4vtpWML._AC_SY741_.jpg",
      rating: 8.8,
      categories: ["Drama", "Romance"],
    },
  ];

  const allCategories = Array.from(new Set(movies.flatMap((m) => m.categories)));

  const { width } = useWindowDimensions();
  const numColumns = 4;
  const cardWidth = width / numColumns - 20;

  // --- State ---
  const [sortBy, setSortBy] = useState<"title" | "rating">("title");
  const [sortDir, setSortDir] = useState<"asc" | "desc">("asc");
  const [filterMinRating, setFilterMinRating] = useState<number>(0);
  const [selectedCategories, setSelectedCategories] = useState<string[]>([]);
  const [search, setSearch] = useState<string>("");
  const [page, setPage] = useState<number>(1);
  const pageSize = 6;

  // --- Filter + Sort + Paginate ---
  const processedMovies = useMemo(() => {
    let list = [...movies];

    // Rating filter
    list = list.filter((movie) => movie.rating >= filterMinRating);

    // Category filter
    if (
      selectedCategories.length > 0 &&
      selectedCategories.length !== allCategories.length
    ) {
      list = list.filter((movie) =>
        movie.categories.some((c) => selectedCategories.includes(c))
      );
    }

    // Search filter
    if (search.trim().length > 0) {
      list = list.filter((movie) =>
        movie.title.toLowerCase().includes(search.toLowerCase())
      );
    }

    // Sort
    if (sortBy === "title") {
      list.sort((a, b) =>
        sortDir === "asc"
          ? a.title.localeCompare(b.title)
          : b.title.localeCompare(a.title)
      );
    } else if (sortBy === "rating") {
      list.sort((a, b) =>
        sortDir === "asc" ? a.rating - b.rating : b.rating - a.rating
      );
    }

    // Pagination
    return list.slice(0, page * pageSize);
  }, [movies, sortBy, sortDir, filterMinRating, selectedCategories, search, page]);

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
      setSelectedCategories([]); // clear
    } else {
      setSelectedCategories(allCategories); // select all
    }
  };

  const toggleSort = (field: "title" | "rating") => {
    if (sortBy === field) {
      setSortDir(sortDir === "asc" ? "desc" : "asc"); // flip direction
    } else {
      setSortBy(field);
      setSortDir("asc"); // default ascending
    }
  };

  const handleRate = (id: string, userRating: number) => {
    console.log(`User rated movie ${id} with ${userRating}`);
  };

  const handleDelete = (id: string) => {
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
        <Pressable onPress={() => toggleSort("title")}>
          <Text style={{ color: sortBy === "title" ? "#007AFF" : "black" }}>
            {sortBy === "title" && sortDir === "asc" ? "Sort A–Z" : "Sort Z–A"}
          </Text>
        </Pressable>
        <Pressable onPress={() => toggleSort("rating")}>
          <Text style={{ color: sortBy === "rating" ? "#007AFF" : "black" }}>
            Rating:
            {sortBy === "rating" && sortDir === "desc"
              ? " Top → Least"
              : " Least → Top"}
          </Text>
        </Pressable>
        <Pressable
          onPress={() =>
            setFilterMinRating((prev) => (prev === 8 ? 0 : 8))
          }
        >
          <Text
            style={{ color: filterMinRating === 8 ? "#007AFF" : "black" }}
          >
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
        data={processedMovies}
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
      {processedMovies.length <
        movies.filter(
          (m) =>
            m.rating >= filterMinRating &&
            (selectedCategories.length === 0 ||
              selectedCategories.length === allCategories.length ||
              m.categories.some((c) => selectedCategories.includes(c))) &&
            (search.trim().length === 0 ||
              m.title.toLowerCase().includes(search.toLowerCase()))
        ).length && (
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
