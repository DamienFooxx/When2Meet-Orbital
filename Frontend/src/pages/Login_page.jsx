import { StyleSheet, Text, TextInput, TouchableOpacity, View, Image, Alert} from 'react-native';
import React, {useState} from 'react';
import { useEffect } from 'react';
import axios from 'axios';
import { GoogleSignin } from '@react-native-google-signin/google-signin';
import AntDesign from 'react-native-vector-icons/AntDesign';
import Ionicons from 'react-native-vector-icons/Ionicons';
import SimpleLineIcons from 'react-native-vector-icons/SimpleLineIcons';
import { BASE_URL } from '../utils/config';
import { colors } from '../utils/colors';
import { fonts } from '../utils/fonts';
import { useNavigation } from '@react-navigation/native';
import AsyncStorage from '@react-native-async-storage/async-storage';

const Login_page = () => {
    // state hooks
    const navigation = useNavigation();
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [showPassword, setShowPassword] = useState(false);

    // Google login
    const handleGoogleLogin = async () => {
        try {
            // ensure Google Play Services are available
            await GoogleSignin.hasPlayServices();

            // prompt user to sign in
            const userInfo = await GoogleSignin.signIn();
            const idToken = userInfo.idToken;

            console.log('Google ID Token:', idToken);

            // send idToken to Django backend
            const response = await axios.post(`${BASE_URL}/api/auth/google/`, {
                access_token: idToken,
            });

            const token = response.data.key;

            // store token in local storage
            await AsyncStorage.setItem('authToken', token);
            await AsyncStorage.setItem('isLoggedIn', 'true');

            // set default header for all axios requests
            axios.defaults.headers.common['Authorization'] = `Token ${token}`;

            Alert.alert('Google login successful');
            navigation.reset({
                index: 0,
                routes: [{ name: 'Main'}],
            });
        } catch (error) {
            const message = 
                error.response?.data?.non_field_errors?.[0] ||
                error.response?.data?.detail ||
                error.message;

            console.error('Google login failed:', message);
            Alert.alert('Google login failed', message);
        }
    };

    useEffect(() => {
        GoogleSignin.configure({
            webClientId: '873882924328-epmb47lfrmsj7jsbc4t656eeeglkb5ld.apps.googleusercontent.com',
            iosClientId: '873882924328-0c4rh1v3m2rvfvqmk6r8rnqidgnmipm1.apps.googleusercontent.com',
            offlineAccess: true,
            forceCodeForRefreshToken: true,
            scopes: ['profile', 'email'],
        });
    }, []);

    //login function
    const handleLogin = async() => {
        if (!email || !password) {
            Alert.alert('Email and password are required');
            return;
        }

        try {
            const response = await axios.post(`${BASE_URL}/api/auth/login/`, {
                email: email,
                password: password,
            });

            if (response.status === 200) {
                const token = response.data.key;
                await AsyncStorage.setItem('authToken', token)
                await AsyncStorage.setItem('isLoggedIn', 'true');

                axios.defaults.headers.common['Authorization'] = `Token ${token}`;

                Alert.alert('Login successful!');
                navigation.navigate('Main');
            }
        } catch (error) {
            console.log('Full error: ', error);
            console.log('Response data: ', error.response?.data);
            Alert.alert('Login failed', JSON.stringify(error.response?.data || error.message));
        }
    };

    const handleGoBack = () => {navigation.navigate('Home')};
    const handleSignup = () => {navigation.navigate('Signup')};

  return (
    <View style = {styles.container}>
      <TouchableOpacity style = {styles.backButtonWrapper} onPress = {handleGoBack}>
        <AntDesign 
        name = {'left'} 
        color = {'white'}
        size = {25}
        />
     </TouchableOpacity>
     <View style = {styles.textContainer}>
           <Text style = {styles.headingText}>Hey,</Text> 
           <Text style = {styles.headingText}>Welcome</Text> 
           <Text style = {styles.headingText}>Back</Text> 
        </View>

        {/* form */}
        <View style = {styles.formContainer}>
            {/* email */}
            <View style = {styles.inputContainer}>
            <Ionicons 
                name = {'mail-outline'} 
                size = {25} 
                color = {colors.containerText}/>
                <TextInput style = {styles.textInput}
                placeholder= 'Enter your email'
                placeholderTextColor={colors.containerText}
                keyboardType = 'email-address'
                autoCapitalize='none'
                value = {email}
                onChangeText={setEmail}
            />
            </View>

            {/* password */}
            <View style = {styles.inputContainer}>
            <SimpleLineIcons
                name = {'lock'} 
                size = {25} 
                color = {colors.containerText}/>
                <TextInput style = {styles.textInput}
                placeholder= 'Enter your password'
                placeholderTextColor={colors.containerText}
                secureTextEntry = {!showPassword}
                autoCapitalize='none'
                value = {password}
                onChangeText={setPassword}
            />
            <TouchableOpacity 
                onPress = {() => {setShowPassword((prev) => !prev);}}>
                <SimpleLineIcons
                    name = {'eye'}
                    size = {20}
                    color = {colors.containerText}
                />
                </TouchableOpacity>
            </View>

            {/* forgot password */}
            <TouchableOpacity>
                <Text style = {styles.forgotPasswordText}>Forgot Password?</Text>
            </TouchableOpacity>

            {/* login */}
            <TouchableOpacity style = {styles.loginButtonWrapper} onPress = {handleLogin}>
                <Text style = {styles.loginText}>Login</Text>
            </TouchableOpacity>

            <Text style ={styles.continueText}>or continue with</Text>
            
            {/* login with Google */}
            <TouchableOpacity style = {styles.googleButtonContainer} onPress = {handleGoogleLogin}>
                <Image 
                    source = {require('../assets/google.png')}
                    style = {styles.googleImage}
                />
                <Text style = {styles.googleText}>Google</Text>
            </TouchableOpacity>
            <View style = {styles.footerContainer}>
                <Text style = {styles.accountText}>Don't have an account?</Text>

                <TouchableOpacity onPress = {handleSignup}>
                    <Text style = {styles.signupText}> Sign up</Text>
                </TouchableOpacity>
                
            </View>
        </View>    
    </View>
  );
};

export default Login_page

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: colors.lightBlue,
        padding: 30,
    },
    backButtonWrapper: {
        marginTop: 30,
        height: 40,
        width: 40,
        backgroundColor: colors.primary,
        borderRadius: 25,
        justifyContent: 'center',
        alignItems: 'center',
    },
    textContainer: {
        marginVertical: 30,
    },
    headingText: {
        fontSize: 40,
        fontFamily: fonts.SemiBold ,
        color: colors.primary,
    },
    formContainer: {
        marginTop: 5,
    },
    inputContainer: {
        borderWidth: 1,
        borderColor: colors.container,
        backgroundColor: colors.container,
        borderRadius: 100,
        paddingHorizontal: 20,
        flexDirection: 'row',
        alignItems: 'center',
        padding: 8,
        marginVertical: 10,
    },
    textInput: {
        flex: 1,
        paddingHorizontal: 10,
        fontFamily: fonts.Light,
    },
    forgotPasswordText: {
        textAlign: 'right',
        color: 'black',
        fontFamily: fonts.Regular,
        marginVertical: 10,
    },
    loginButtonWrapper: {
        backgroundColor: colors.primary,
        borderWidth: 2,
        borderRadius: 100,
        justifyContent: 'center',
        alignItems: 'center',
        marginTop: 50,
        marginBottom: 8,
    },
    loginText: {
        color: colors.white,
        fontSize: 18,
        fontFamily: fonts.SemiBold,
        textAlign: 'center',
        padding: 10,
    },
    continueText: {
        textAlign: 'center',
        marginVertical: 30,
        fontSize: 12,
        fontFamily: fonts.Regular,
    },
    googleButtonContainer: {
        flexDirection: 'row',
        borderWidth: 2,
        borderColor: colors.container,
        backgroundColor: colors.container,
        borderRadius: 100,
        justifyContent: 'center',
        alignItems: 'center',
        padding: 10,
        gap: 10,
        marginTop: 8,
    },
    googleImage: {
        height: 18,
        width: 17,
    },
    googleText: {
        fontSize: 15,
        fontFamily: fonts.SemiBold,
        color: colors.primary,
    },
    footerContainer: {
        flexDirection: 'row',
        justifyContent: 'center',
        alignItems: 'center',
        marginVertical: 20,
        gap: 5,
    },
    accountText: {
        color: 'black',
        fontFamily: fonts.Regular,
    },
    signupText: {
        color: 'black',
        fontFamily: fonts.SemiBold,
    },
});