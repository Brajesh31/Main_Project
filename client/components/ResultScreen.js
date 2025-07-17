import React from "react";
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  Dimensions,
  Animated,
} from "react-native";
import { LineChart } from "react-native-chart-kit";

// Helper function to format time in 12-hour format
const formatTo12Hour = (time) => {
  const [hour, minute] = time.split(":");
  const hourInt = parseInt(hour, 10);
  const isPM = hourInt >= 12;
  const formattedHour = hourInt % 12 || 12; // Convert hour to 12-hour format
  const period = isPM ? "PM" : "AM";
  return `${formattedHour}:${minute} ${period}`;
};

const ResultScreen = ({ route }) => {
  const { results } = route.params;

  // Get dimensions for responsive design
  const screenWidth = Dimensions.get("window").width;

  // Animated value for climate information
  const fadeAnim = new Animated.Value(0);

  React.useEffect(() => {
    Animated.timing(fadeAnim, {
      toValue: 1,
      duration: 1000,
      useNativeDriver: true,
    }).start();
  }, []);

  // Calculate key insights
  const maxPower = Math.max(...results.map((item) => item.predicted_power));
  const minPower = Math.min(...results.map((item) => item.predicted_power));
  const avgPower =
    results.reduce((sum, item) => sum + item.predicted_power, 0) /
    results.length;

  const maxPowerTime = results.find(
    (item) => item.predicted_power === maxPower
  ).timestamp;

  // Extract current climate info (from first data point)
  const currentClimate = results[0];

  // Prepare chart data (subset of results for clarity)
  const reducedResults = results.filter((_, index) => index % 6 === 0); // Show every 6th value
  const labels = reducedResults.map(
    (item) => formatTo12Hour(item.timestamp.split(" ")[1]) // Format time to 12-hour
  );
  const data = reducedResults.map((item) => item.predicted_power);

  return (
    <ScrollView style={styles.container}>
      <Text style={styles.title}>Prediction Results</Text>

      {/* Animated Climate Information */}
      <Animated.View
        style={[
          styles.climateContainer,
          {
            opacity: fadeAnim,
          },
        ]}
      >
        <Text style={styles.climateTitle}>Current Climate</Text>
        <Text style={styles.climateText}>
          <Text style={styles.bold}>Temperature:</Text>{" "}
          {currentClimate.temperature.toFixed(2)} °C
        </Text>
        <Text style={styles.climateText}>
          <Text style={styles.bold}>Wind Speed:</Text>{" "}
          {currentClimate.wind_speed.toFixed(2)} m/s
        </Text>
        <Text style={styles.climateText}>
          <Text style={styles.bold}>Humidity:</Text> {currentClimate.humidity} %
        </Text>
        <Text style={styles.climateText}>
          <Text style={styles.bold}>Pressure:</Text> {currentClimate.pressure}{" "}
          hPa
        </Text>
      </Animated.View>

      {/* Insights Section */}
      <View style={styles.insightsContainer}>
        <Text style={styles.insightText}>
          <Text style={styles.bold}>Max Power:</Text> {maxPower.toFixed(2)} kW
          {"\n"}
          <Text style={styles.bold}>Time:</Text>{" "}
          {formatTo12Hour(maxPowerTime.split(" ")[1])}
        </Text>
        <Text style={styles.insightText}>
          <Text style={styles.bold}>Min Power:</Text> {minPower.toFixed(2)} kW
        </Text>
        <Text style={styles.insightText}>
          <Text style={styles.bold}>Average Power:</Text> {avgPower.toFixed(2)}{" "}
          kW
        </Text>
      </View>

      {/* Line Chart */}
      <LineChart
        data={{
          labels, // X-axis labels
          datasets: [{ data }], // Y-axis data
        }}
        width={screenWidth - 40} // Dynamic width
        height={250}
        yAxisSuffix=" kW" // Add a suffix to Y-axis values
        yAxisInterval={1} // Set interval for Y-axis for better readability
        chartConfig={{
          backgroundGradientFrom: "#e5f6ff",
          backgroundGradientTo: "#b3e5fc",
          decimalPlaces: 2, // Number of decimal places for Y-axis values
          color: (opacity = 1) => `rgba(0, 128, 255, ${opacity})`, // Line color
          labelColor: (opacity = 1) => `rgba(0, 0, 0, ${opacity})`, // X and Y label color
          style: {
            borderRadius: 16,
          },
          propsForLabels: {
            fontSize: 10, // Set the font size of axis labels
          },
        }}
        style={styles.chart}
        bezier // Use a smooth curve
      />
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 20,
    backgroundColor: "#fff",
  },
  title: {
    fontSize: 22,
    fontWeight: "bold",
    marginBottom: 15,
    textAlign: "center",
  },
  climateContainer: {
    marginBottom: 20,
    padding: 15,
    borderWidth: 1,
    borderRadius: 8,
    borderColor: "#ddd",
    backgroundColor: "#f0f8ff",
  },
  climateTitle: {
    fontSize: 18,
    fontWeight: "bold",
    marginBottom: 10,
  },
  climateText: {
    fontSize: 16,
    marginBottom: 5,
  },
  bold: {
    fontWeight: "bold",
  },
  insightsContainer: {
    marginBottom: 20,
    padding: 15,
    borderWidth: 1,
    borderRadius: 8,
    borderColor: "#ddd",
    backgroundColor: "#f0f8ff",
  },
  insightText: {
    fontSize: 16,
    marginBottom: 10,
    lineHeight: 24,
  },
  chart: {
    marginVertical: 20,
    borderRadius: 16,
  },
});

export default ResultScreen;
