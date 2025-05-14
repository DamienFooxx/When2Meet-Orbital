import { StyleSheet, Text, TextInput, TouchableOpacity, View, Image, Alert} from 'react-native';
import React, {useState} from 'react';
import axios from 'axios';
import AntDesign from "react-native-vector-icons/AntDesign";
import Ionicons from "react-native-vector-icons/Ionicons";
import SimpleLineIcons from "react-native-vector-icons/SimpleLineIcons";
import { colors } from '../utils/colors';
import { fonts } from '../utils/fonts';
import { BASE_URL } from '../utils/config';
import { useNavigation } from '@react-navigation/native';

const Signup_page = () => {
    {/* state hooks */}
    const navigation = useNavigation();
    const [email, setEmail] = useState('');
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [showPassword, setShowPassword] = useState(false);
    const [showConfirmPassword, setShowConfirmPassword] = useState(false);

    {/* sign up function */}
    const handleSignupRequest = async() => {
        if (!username || !email || !password || !confirmPassword) {
            Alert.alert("All fields are required.");
        }

        if (password != confirmPassword) {
            Alert.alert("Passwords do not match.");
            return;
        }

        console.log({
            username,
            email,
            password1: password,
            password2: confirmPassword,
        });

        try {
            const response = await axios.post(`${BASE_URL}/api/auth/registration/`, {
                username,
                email,
                password1: password,
                password2: confirmPassword,
            });

            if (response.status === 201 || response.status === 200) {
                Alert.alert("Signup successful");
                navigation.navigate("Login");
            }
        } catch (error) {
            if (error.response) {
                console.log("signup failed - response:", error.response.data);
                Alert.alert("signup failed", JSON.stringify(error.response.data));
              } else if (error.request) {
                console.log("signup failed - no response:", error.request);
                Alert.alert("signup failed", "no response from server");
              } else {
                console.log("signup failed - other error:", error.message);
                Alert.alert("signup failed", error.message);
              }
        }
    };

    const handleGoBack = () => {
        navigation.goBack();
    };

    const handleLogin = () => {
        navigation.navigate("Login")
    };

  return (
    <View style = {styles.container}>
      <TouchableOpacity style = {styles.backButtonWrapper} onPress = {handleGoBack}>
        <AntDesign 
        name = {"left"} 
        color = {colors.primary}
        size = {25}
        />
     </TouchableOpacity>

     <View style = {styles.textContainer}>
           <Text style = {styles.headingText}>Let's get</Text> 
           <Text style = {styles.headingText}>Started</Text> 
    </View>
        
    {/* form */}
    <View style = {styles.formContainer}>
        {/* Username */}
        <View style = {styles.inputContainer}>
            <AntDesign
                name = {"user"}
                size = {22}
                color = {colors.secondary}
            />
            <TextInput
                style = {styles.textInput}
                placeholder='Enter your username'
                placeholderTextColor={colors.secondary}
                autoCapitalize='none'
                value = {username}
                onChangeText={setUsername}
                textContentType='none'
                autoComplete="off"
                importantForAutofill='no'
                enablesReturnKeyAutomatically={false}
            />
        </View>

        {/* Email */}
        <View style = {styles.inputContainer}>
            <Ionicons 
                name = {"mail-outline"} 
                size = {25} 
                color = {colors.secondary}/>
                <TextInput style = {styles.textInput}
                value = {email}
                onChangeText={setEmail}
                placeholder= "Enter your email"
                placeholderTextColor={colors.secondary}
                keyboardType = "email-address"
                autoCapitalize='none'
                textContentType='none'
                autoComplete="off"
                importantForAutofill='no'
            />
            </View>

            {/* Password */}
            <View style = {styles.inputContainer}>
            <SimpleLineIcons
                name = {"lock"} 
                size = {25} 
                color = {colors.secondary}/>
                <TextInput style = {styles.textInput}
                placeholder= "Enter your password"
                placeholderTextColor={colors.secondary}
                secureTextEntry = {!showPassword}
                value = {password}
                onChangeText={setPassword}
                autoCapitalize='none'
                textContentType='none'
                autoComplete="off"
                importantForAutofill='no'
            />
            <TouchableOpacity 
                onPress = {() => {
                    setShowPassword((prev) => !prev);
                }}
            >
                <SimpleLineIcons
                    name = {"eye"}
                    size = {20}
                    color = {colors.secondary}
                />
                </TouchableOpacity>
            </View>

            {/* confirm passwrord */}
            <View style = {styles.inputContainer}>
                <SimpleLineIcons
                    name = {"lock"}
                    size = {25}
                    colors = {colors.secondary}
            />
            <TextInput
                style = {styles.textInput}
                placeholder='Confirm your password'
                placeholderTextColor={colors.secondary}
                secureTextEntry={!showConfirmPassword}
                value = {confirmPassword}
                onChangeText={setConfirmPassword}
                autoCapitalize='none'
                textContentType='none'
                autoComplete="off"
                importantForAutofill='no'
            />
            <TouchableOpacity onPress = {() => setShowConfirmPassword(prev => !prev)}>
                <SimpleLineIcons
                    name = {"eye"}
                    size = {20}
                    color = {colors.secondary}
                />
            </TouchableOpacity>
            </View>
        
            {/* sign up button */}
            <TouchableOpacity style = {styles.signinContainer} onPress = {handleSignupRequest}>
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
        backgroundColor: colors.white,
        padding: 30,
        marginTop: 30,
    },
    backButtonWrapper: {
        height: 40,
        width: 40,
        backgroundColor: colors.gray,
        borderRadius: 25,
        justifyContent: "center",
        alignItems: "center",
    },
    textContainer: {
        marginVertical: 30,
    },
    headingText: {
        fontSize: 40,
        fontFamily: fonts.SemiBold ,
        color: colors.blue,
    },
    formContainer: {
        marginTop: 5,
    },
    inputContainer: {
        borderWidth: 1,
        borderColor: colors.secondary,
        borderRadius: 100,
        paddingHorizontal: 20,
        flexDirection: "row",
        alignItems: "center",
        padding: 10,
        marginVertical: 10,
    },
    textInput: {
        flex: 1,
        paddingHorizontal: 10,
        fontFamily: fonts.Light,
    },
    forgotPasswordText: {
        textAlign: "right",
        color: colors.primary,
        fontFamily: fonts.SemiBold,
        marginVertical: 10,
    },
    loginButtonWrapper: {
        backgroundColor: colors.primary,
        borderWidth: 2,
        borderRadius: 100,
        justifyContent: "center",
        alignItems: "center",
        marginTop: 50,
        marginBottom: 8,
    },
    signinContainer: {
        borderWidth: 1,
        borderColor: colors.secondary,
        borderRadius: 100,
        paddingHorizontal: 10,
        justifyContent: "center",
        alignItems: "center",
        padding: 10,
        marginTop: 90,
    },
    signupText: {
        color: colors.primary,
        fontSize: 18,
        fontFamily: fonts.SemiBold,
        textAlign: "center",
        padding: 10,
    },
    footerContainer: {
        flexDirection: "row",
        justifyContent: "center",
        alignItems: "center",
        marginVertical: 10,
        gap: 5,
    },
    accountText: {
        color: colors.primary,
        fontFamily: fonts.Regular,
    },
    loginText: {
        color: colors.primary,
        fontFamily: fonts.SemiBold,
    },
});