import React, { useState, useEffect } from "react";
import { View, Text, Image, Pressable } from "react-native";


type MediaCardProps = {
  id: string;
  title: string;
  posterUrl: string;
  rating: number;
  userRating?: number | null;
  onRate: (id: string, userRating: number) => void;
  onDelete: (id: string) => void;
};

export default function MediaCard({
  id,
  title,
  posterUrl,
  rating,
  userRating: initialUserRating,
  onRate,
  onDelete,
}: MediaCardProps) {
  const [userRating, setUserRating] = useState<number | null>(null);

  useEffect(() => {
    setUserRating(initialUserRating ?? null);
  }, [initialUserRating]);

  const handleRate = (value: number) => {
    setUserRating(value);
    onRate(id, value);
  };

  return (
    <View
      style={{
        borderWidth: 1,
        borderColor: "#ccc",
        borderRadius: 12,
        padding: 8,
        backgroundColor: "white",
        shadowColor: "#000",
        shadowOpacity: 0.1,
        shadowOffset: { width: 0, height: 2 },
        shadowRadius: 5,
        elevation: 3,
        flex: 1,
      }}
    >
      {/* Top row: title + delete */}
      <View
        style={{
          flexDirection: "row",
          justifyContent: "space-between",
          alignItems: "center",
          marginBottom: 8,
        }}
      >
        <Text
          style={{ fontSize: 14, fontWeight: "bold", flex: 1 }}
          numberOfLines={1}
        >
          {title}
        </Text>
        <Pressable
          onPress={() => onDelete(id)}
          style={{
            backgroundColor: "#f55",
            borderRadius: 12,
            paddingHorizontal: 6,
            paddingVertical: 2,
            marginLeft: 8,
          }}
        >
          <Text style={{ color: "white", fontWeight: "bold" }}>X</Text>
        </Pressable>
      </View>

      {/* Poster in fixed aspect ratio, scales down if needed */}
      <View
        style={{
          width: "100%",
          aspectRatio: 2 / 3,
          borderRadius: 10,
          overflow: "hidden",
          marginBottom: 8,
          justifyContent: "center",
          alignItems: "center",
          backgroundColor: "#eee",
        }}
      >
        <Image
          source={{ uri: posterUrl }}
          style={{ width: "100%", height: "100%" }}
          resizeMode="contain" // scale down if needed
        />
      </View>

      {/* Ratings */}
      <Text style={{ fontSize: 13, color: "gray" }}>
        ⭐ Average: {rating.toFixed(1)}
      </Text>
      <Text style={{ fontSize: 13, color: "#007AFF", marginTop: 2 }}>
        Your Rating: {userRating !== null ? userRating : "-"}
      </Text>

      {/* Buttons */}
      <View
        style={{
          flexDirection: "row",
          flexWrap: "wrap",
          marginTop: 8,
        }}
      >
        {Array.from({ length: 11 }, (_, i) => (
          <Pressable
            key={i}
            onPress={() => handleRate(i)}
            style={{
              backgroundColor: userRating === i ? "#007AFF" : "#eee",
              paddingHorizontal: 8,
              paddingVertical: 4,
              borderRadius: 6,
              margin: 2,
            }}
          >
            <Text style={{ color: userRating === i ? "white" : "black" }}>
              {i}
            </Text>
          </Pressable>
        ))}
      </View>
    </View>
  );
}
