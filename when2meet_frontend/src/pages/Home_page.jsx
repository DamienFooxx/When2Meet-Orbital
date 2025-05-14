import { Image, StyleSheet, Text, View, Dimensions, TouchableOpacity } from 'react-native';
import React from 'react';
import { colors } from '../utils/colors';
import { fonts } from '../utils/fonts';
import { useNavigation } from '@react-navigation/native';

const { height } = Dimensions.get('window');

const Home_page = () => {
    const navigation = useNavigation()
    const handleLogin = () => {
        navigation.navigate("Login")
    };

    const handleSignup = () => {
        navigation.navigate("Signup")
    }
    ;
  return (
    <View style = {styles.container}>
      <Image source = {require("../assets/flower.png")} style = {styles.bannerImage}/>
      <Text style = {styles.title}>When2Meet</Text>
      <Text style = {styles.subtitle}>One Link to Share, One Time to Meet.</Text>
      <View style = {styles.buttonContainer}>
        <TouchableOpacity style = {[
            styles.loginButtonWrapper,
        {backgroundColor: colors.primary},
    ]}
    onPress={handleLogin}
    >
            <Text style = {styles.loginButtonText}>Login</Text>
        </TouchableOpacity>
        <TouchableOpacity style = {[styles.loginButtonWrapper]} onPress = {handleSignup}>
            <Text style = {styles.signupButtonText}>Sign-up</Text>
        </TouchableOpacity>

      </View>
    </View>
  );
};

export default Home_page

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: colors.white,
        alignItems: "center",
    },
    bannerImage: {
        height: height * 0.60,
        width: 250,
        resizeMode: 'contain',
        marginTop: 30, 
    },
    title: {
        fontSize: 40,
        fontFamily: fonts.SemiBold,
        paddingHorizontal: 20,
        color: colors.primary,
        textAlign: "center",
        marginTop: 0,
    },
    subtitle: {
        fontSize: 20,
        textAlign: "center",
        color: colors.secondary,
        fontFamily: fonts.Medium,
        paddingHorizontal: 20,
        marginVertical: 10,
    },
    buttonContainer: {
        marginTop: 20,
        flexDirection: "row",
        borderWidth: 1,
        borderColor: colors.primary,
        width: "90%",
        height: 60,
        borderRadius: 98,
    },
    loginButtonWrapper: {
        justifyContent: "center",
        alignItems: "center",
        width: "50%",
        backgroundColor: colors.primary,
        borderRadius: 98,
    },
    loginButtonText: {
        color: colors.primary,
        fontSize: 18,
        fontFamily: fonts.SemiBold,
    },
    signupButtonText: {
        fontSize: 18,
        fontFamily: fonts.SemiBold,
    },
});