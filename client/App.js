import React from "react";
import { NavigationContainer } from "@react-navigation/native";
import { createStackNavigator } from "@react-navigation/stack";
import HomeScreen from "./components/HomeScreen";
import ResultScreen from "./components/ResultScreen";

const Stack = createStackNavigator();

const App = () => {
  return (
    <NavigationContainer>
      <Stack.Navigator initialRouteName="HomeScreen">
        <Stack.Screen
          name="HomeScreen"
          component={HomeScreen}
          options={{ title: "Home" }}
        />
        <Stack.Screen
          name="ResultScreen"
          component={ResultScreen}
          options={{ title: "Results" }}
        />
      </Stack.Navigator>
    </NavigationContainer>
  );
};

export default App;
