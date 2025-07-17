import React, { useState } from "react";
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  Alert,
  ActivityIndicator,
} from "react-native";
import * as Location from "expo-location";
import { LinearGradient } from "expo-linear-gradient"; // For gradient background

const HomeScreen = ({ navigation }) => {
  const [latitude, setLatitude] = useState("");
  const [longitude, setLongitude] = useState("");
  const [loading, setLoading] = useState(false); // State for loading indicator

  const handleGetLocation = async () => {
    try {
      const { status } = await Location.requestForegroundPermissionsAsync();
      if (status !== "granted") {
        Alert.alert("Permission Denied", "Location permission is required.");
        return;
      }
      const location = await Location.getCurrentPositionAsync({});
      setLatitude(location.coords.latitude.toString());
      setLongitude(location.coords.longitude.toString());
    } catch (error) {
      Alert.alert("Error", "Failed to fetch location. Please try again.");
    }
  };

  const handlePredict = async () => {
    if (!latitude || !longitude) {
      Alert.alert("Error", "Please enter both latitude and longitude.");
      return;
    }

    setLoading(true); // Start loading
    setTimeout(async () => {
      try {
        const response = await fetch(
          `http://192.168.129.248:5000/predict?latitude=${latitude}&longitude=${longitude}`
        );
        const data = await response.json();

        setLoading(false); // Hide loading indicator
        if (response.ok) {
          navigation.navigate("ResultScreen", { results: data.data });
        } else {
          Alert.alert("Error", data.error || "Unable to fetch predictions.");
        }
      } catch (error) {
        setLoading(false); // Hide loading indicator
        Alert.alert("Error", "Failed to fetch data. Please check your server.");
      }
    }, 3000); // Add a delay of 3 seconds
  };
  return (
    <LinearGradient
      colors={["#e0f7fa", "#b2ebf2", "#80deea"]}
      style={styles.container}
    >
      <Text style={styles.title}>Wind Power Prediction</Text>

      <TextInput
        style={styles.input}
        placeholder="Enter Latitude"
        keyboardType="numeric"
        value={latitude}
        onChangeText={setLatitude}
      />
      <TextInput
        style={styles.input}
        placeholder="Enter Longitude"
        keyboardType="numeric"
        value={longitude}
        onChangeText={setLongitude}
      />

      <TouchableOpacity style={styles.button} onPress={handleGetLocation}>
        <Text style={styles.buttonText}>Use Current Location</Text>
      </TouchableOpacity>

      <TouchableOpacity
        style={[styles.button, { backgroundColor: "#0277bd" }]}
        onPress={handlePredict}
      >
        <Text style={styles.buttonText}>Predict</Text>
      </TouchableOpacity>

      {loading && (
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color="#0277bd" />
          <Text style={styles.loadingText}>Fetching Predictions...</Text>
        </View>
      )}
    </LinearGradient>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
    padding: 20,
  },
  title: {
    fontSize: 28,
    fontWeight: "bold",
    color: "#004d40",
    marginBottom: 20,
  },
  input: {
    width: "80%",
    height: 50,
    borderWidth: 1,
    borderRadius: 8,
    paddingHorizontal: 10,
    marginBottom: 15,
    fontSize: 16,
    borderColor: "#004d40",
    backgroundColor: "#fff",
  },
  button: {
    backgroundColor: "#4CAF50",
    paddingVertical: 15,
    paddingHorizontal: 40,
    borderRadius: 8,
    marginTop: 10,
  },
  buttonText: {
    color: "#FFF",
    fontSize: 18,
    fontWeight: "bold",
  },
  loadingContainer: {
    marginTop: 20,
    alignItems: "center",
  },
  loadingText: {
    fontSize: 16,
    color: "#0277bd",
    marginTop: 10,
  },
});

export default HomeScreen;
