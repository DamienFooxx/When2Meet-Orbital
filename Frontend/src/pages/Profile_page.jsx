import { StyleSheet, Text, View, Image, TouchableOpacity, Alert } from 'react-native';
import React from 'react';
import { useNavigation } from '@react-navigation/native';
import Ionicons from 'react-native-vector-icons/Ionicons';
import { colors } from '../utils/colors';
import { fonts } from '../utils/fonts';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { GoogleSignin } from '@react-native-google-signin/google-signin';

const Profile_page = ({ navigation }) => {

    const handleLogout = async () => {
        try {
            // clear stored auth token and flags
            await AsyncStorage.removeItem('authToken');
            await AsyncStorage.removeItem('isLoggedIn');

            // revoke and sign out from google
            await GoogleSignin.revokeAccess();
            await GoogleSignin.signOut();

            // navigate to login
            navigation.replace('Login');
        } catch (error) {
            console.error('Logout failed:', error);
            Alert.alert('Error', 'Failed to sign out. Please try again');
        }
    }
    

  return (
    <View style = {styles.container}>
      <View style = {styles.topBar}>
        <TouchableOpacity onPress = {() => navigation.goBack()}>
          <Ionicons name = "chevron-back-outline" size = {25} color = {colors.primary} />
        </TouchableOpacity>

        <TouchableOpacity>
          <Ionicons name = "share-outline" size = {25} color = "black"/>
        </TouchableOpacity>
      </View>
      <View style = {styles.profileHeader}>
          <Ionicons name = "person-outline" size = {60} color = {'black'}/>
          <Text style = {styles.username}>username</Text>
          <Text style = {styles.email}>xxxxx@gmail.com</Text>
      </View>

      {/* Options */}
      <TouchableOpacity style = {styles.optionButton}>
        <Text style = {styles.optionText}>Account Details</Text>
      </TouchableOpacity>

      <TouchableOpacity style = {styles.optionButton}>
        <Text style = {styles.optionText}>Activity/History</Text>
      </TouchableOpacity>

      <TouchableOpacity style = {styles.optionButton}>
        <Text style = {styles.optionText}>Security & Support</Text>
      </TouchableOpacity>

      <TouchableOpacity style = {styles.optionButton}>
        <Text style = {styles.optionText}>About Us</Text>
      </TouchableOpacity>

      {/* Logout */}
      <TouchableOpacity style = {styles.signOutButton} onPress = {handleLogout}>
        <Text style = {styles.signOutText}>Sign out</Text>
      </TouchableOpacity>
    </View>
  );
};

export default Profile_page

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: colors.white,
        padding: 30,
        paddingTop: 80,
    },

    topBar: {
      flexDirection: 'row',
      alignItems: 'center',
      justifyContent: 'space-between',
      paddingHorizontal: 10,
      paddingBottom: 100,
    },

    profileHeader: {
        alignItems: 'center',
        marginBottom: 30,
    },
    username: {
        fontSize: 20,
        fontFamily: fonts.SemiBold,
        marginTop: 8,
    },
    email: {
        fontSize: 14,
        fontFamily: fonts.Regular,
        color: colors.containerText,
    },
    optionButton: {
        backgroundColor: colors.lightBlue,
        borderRadius: 10,
        padding: 15,
        marginVertical: 5,
    },
    optionText: {
        fontSize: 16,
        fontFamily: fonts.SemiBold,
        color: colors.primary,
    },
    signOutButton: {
        backgroundColor: colors.primary,
        borderRadius: 10,
        padding: 15,
        marginTop: 25,
    },
    signOutText: {
        color: 'white',
        textAlign: 'center',
        fontSize: 16,
        fontFamily: fonts.SemiBold,
    },
})