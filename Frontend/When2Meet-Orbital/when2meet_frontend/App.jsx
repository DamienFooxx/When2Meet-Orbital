import { StyleSheet, Text, View } from 'react-native';
import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import Home_page from './src/pages/Home_page';
import Login_page from './src/pages/Login_page';
import Signup_page from './src/pages/Signup_page';
import Main_page from './src/pages/Main_page';

const Stack = createNativeStackNavigator();

const App = () => {
  return (
    <NavigationContainer>
      <Stack.Navigator 
      screenOptions = {{
        headerShown: false
        }}
        > 
        <Stack.Screen name={"Home"} component = {Home_page}/>
        <Stack.Screen name={"Login"} component = {Login_page}/>
        <Stack.Screen name={"Signup"} component = {Signup_page}/>
        <Stack.Screen name={"Main"} component = {Main_page}/>
      </Stack.Navigator>
    </NavigationContainer>
  )
}

export default App

const styles = StyleSheet.create({})