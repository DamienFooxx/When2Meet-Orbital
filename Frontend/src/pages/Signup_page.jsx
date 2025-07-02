import { StyleSheet, Text, TextInput, TouchableOpacity, View, Image, Alert} from 'react-native';
import React, {useState} from 'react';
import axios from 'axios';
import AntDesign from 'react-native-vector-icons/AntDesign';
import Ionicons from 'react-native-vector-icons/Ionicons';
import SimpleLineIcons from 'react-native-vector-icons/SimpleLineIcons';
import { colors } from '../utils/colors';
import { fonts } from '../utils/fonts';
import { API_BASE } from '../utils/config';
import { useNavigation } from '@react-navigation/native';
import { useUser } from '../context/UserContext';

const API_PREFIX = 'https://when2meetimage-686579494898.asia-southeast1.run.app';
  
const Signup_page = () => {
    {/* state hooks */}
    const navigation = useNavigation();
    const [email, setEmail] = useState('');
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [showPassword, setShowPassword] = useState(false);
    const [showConfirmPassword, setShowConfirmPassword] = useState(false);
    const { login } = useUser();

    {/* sign up function */}
    const handleSignupRequest = async() => {
        if (!username || !email || !password || !confirmPassword) {
            Alert.alert('All fields are required.');
        }

        if (password != confirmPassword) {
            Alert.alert('Passwords do not match.');
            return;
        }

        console.log({
            username,
            email,
            password1: password,
            password2: confirmPassword,
        });

        try {
            const response = await axios.post(`${API_BASE}/auth/registration/`, {
                username,
                email,
                password1: password,
                password2: confirmPassword,
            });

            if (response.status === 201 || response.status === 200) {
                const userData = { username, email };
                await login(userData);
                Alert.alert('Signup successful');
                navigation.navigate('Login');
            }
        } catch (error) {
            if (error.response) {
                console.log('signup failed - response:', error.response.data);
                Alert.alert('signup failed', JSON.stringify(error.response.data));
              } else if (error.request) {
                console.log('signup failed - no response:', error.request);
                Alert.alert('signup failed', 'no response from server');
              } else {
                console.log('signup failed - other error:', error.message);
                Alert.alert('signup failed', error.message);
              }
        }
    };

    const handleGoBack = () => {
        navigation.goBack();
    };

    const handleLogin = () => {
        navigation.navigate('Login')
    };

  return (
    <View style = {styles.container}>
      <TouchableOpacity style = {styles.backButtonWrapper} onPress = {handleGoBack}>
        <AntDesign 
        name = {'left'} 
        color = {colors.white}
        size = {25}
        />
     </TouchableOpacity>

     <View style = {styles.headingContainer}>
           <Text style = {styles.headingText}>Let's get</Text> 
           <Text style = {styles.headingText}>Started</Text> 
    </View>
        
    {/* form */}
    <View style = {styles.formContainer}>
        {/* Username */}
        <View style = {styles.inputContainer}>
            <AntDesign
                name = {'user'}
                size = {22}
                color = {colors.containerText}
            />
            <TextInput
                style = {styles.textInput}
                placeholder='Enter your username'
                placeholderTextColor={colors.containerText}
                autoCapitalize='none'
                value = {username}
                onChangeText={setUsername}
                textContentType='none'
                autoComplete='off'
                importantForAutofill='no'
                enablesReturnKeyAutomatically={false}
            />
        </View>

        {/* Email */}
        <View style = {styles.inputContainer}>
            <Ionicons 
                name = {'mail-outline'} 
                size = {25} 
                color = {colors.containerText}/>
                <TextInput style = {styles.textInput}
                value = {email}
                onChangeText={setEmail}
                placeholder= 'Enter your email'
                placeholderTextColor={colors.containerText}
                keyboardType = 'email-address'
                autoCapitalize='none'
                textContentType='none'
                autoComplete='off'
                importantForAutofill='no'
            />
            </View>

            {/* Password */}
            <View style = {styles.inputContainer}>
            <SimpleLineIcons
                name = {'lock'} 
                size = {25} 
                color = {colors.containerText}/>
                <TextInput style = {styles.textInput}
                placeholder= 'Enter your password'
                placeholderTextColor={colors.containerText}
                secureTextEntry = {!showPassword}
                value = {password}
                onChangeText={setPassword}
                autoCapitalize='none'
                textContentType='none'
                autoComplete='off'
                importantForAutofill='no'
            />
            <TouchableOpacity 
                onPress = {() => {
                    setShowPassword((prev) => !prev);
                }}
            >
                <SimpleLineIcons
                    name = {'eye'}
                    size = {20}
                    color = {colors.containerText}
                />
                </TouchableOpacity>
            </View>

            {/* confirm passwrord */}
            <View style = {styles.inputContainer}>
                <SimpleLineIcons
                    name = {'lock'}
                    size = {25}
                    color = {colors.containerText}
            />
            <TextInput
                style = {styles.textInput}
                placeholder='Confirm your password'
                placeholderTextColor={colors.containerText}
                secureTextEntry={!showConfirmPassword}
                value = {confirmPassword}
                onChangeText={setConfirmPassword}
                autoCapitalize='none'
                textContentType='none'
                autoComplete='off'
                importantForAutofill='no'
            />
            <TouchableOpacity onPress = {() => setShowConfirmPassword(prev => !prev)}>
                <SimpleLineIcons
                    name = {'eye'}
                    size = {20}
                    color = {colors.containerText}
                />
            </TouchableOpacity>
            </View>
        
            {/* sign up button */}
            <TouchableOpacity style = {styles.signUpContainer} onPress = {handleSignupRequest}>
                <Text style = {styles.signupText}>Signup</Text>
            </TouchableOpacity>

            {/* footer */}
            <View style = {styles.footerContainer}>
                <Text style = {styles.accountText}>Already have an account?</Text>
                <TouchableOpacity onPress = {handleLogin}>
                    <Text style = {styles.loginText}>Log in</Text>
                </TouchableOpacity>
            </View>
        </View>    
    </View>
  );
};

export default Signup_page

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: colors.lightBlue,
        padding: 30,
    },

    backButtonWrapper: {
        height: 40,
        width: 40,
        backgroundColor: colors.primary,
        borderRadius: 25,
        justifyContent: 'center',
        alignItems: 'center',
        marginTop: 30,
    },
    headingContainer: {
        marginTop: 60,
        marginBottom: 60,
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
        padding: 10,
        marginVertical: 8,
    },
    textInput: {
        flex: 1,
        paddingHorizontal: 10,
        fontFamily: fonts.Light,
    },

    signUpContainer: {
        borderWidth: 1,
        borderColor: colors.primary,
        backgroundColor: colors.primary,
        borderRadius: 100,
        paddingHorizontal: 10,
        justifyContent: 'center',
        alignItems: 'center',
        padding: 10,
        marginTop: 90,
    },
    signupText: {
        color: colors.white,
        fontSize: 18,
        fontFamily: fonts.SemiBold,
        textAlign: 'center',
        padding: 10,
    },
    footerContainer: {
        flexDirection: 'row',
        justifyContent: 'center',
        alignItems: 'center',
        marginVertical: 10,
        gap: 5,
    },
    accountText: {
        color: 'black',
        fontFamily: fonts.Regular,
    },
    loginText: {
        color: 'black',
        fontFamily: fonts.SemiBold,
    },
});