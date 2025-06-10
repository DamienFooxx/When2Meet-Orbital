import { StyleSheet, Text, View } from 'react-native';
import React, { useState, useEffect } from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import AsyncStorage from '@react-native-async-storage/async-storage';

// pages
import Home_page from './src/pages/Home_page';
import Login_page from './src/pages/Login_page';
import Signup_page from './src/pages/Signup_page';
import Main_page from './src/pages/Main_page';
import Profile_page from './src/pages/Profile_page';
import CreateGroup_page from './src/pages/CreateGroup_page';

// context
import { UserProvider } from './src/context/UserContext';

const Stack = createNativeStackNavigator();

const App = () => {
  const [initialRoute, setInitialRoute] = useState(null);

  useEffect(() => {
    const checkLoginStatus = async () => {
      const loggedIn = await AsyncStorage.getItem('isLoggedIn');
      setInitialRoute(loggedIn === 'true' ? 'Main' : 'Home');
    };
    checkLoginStatus();
  }, []);

  if (initialRoute === null) return null;

  return (
    <UserProvider>
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
            <Stack.Screen name={"Profile"} component = {Profile_page}/>
            <Stack.Screen name={"CreateGroup"} component = {CreateGroup_page}/> 
        </Stack.Navigator>
        </NavigationContainer>
    </UserProvider>
  )
}

export default App

const styles = StyleSheet.create({})
