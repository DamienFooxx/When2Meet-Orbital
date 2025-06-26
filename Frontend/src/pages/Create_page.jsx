import { StyleSheet, Text, View, TouchableOpacity } from 'react-native'
import React from 'react'
import { colors } from '../utils/colors';
import { fonts } from '../utils/fonts';
import { useNavigation } from '@react-navigation/native';

const Create_page = () => {
    const navigation = useNavigation();

  return (
    <View style = {styles.container}>
      <Text style = {styles.title}>What would you like to create?</Text>

      <TouchableOpacity
        style = {styles.optionButton}
        onPress = {() => navigation.navigate('CreateEvent')}
      >
        <Text style = {styles.optionText}>Create Event</Text>
      </TouchableOpacity>

      <TouchableOpacity
        style = {styles.optionButton}
        onPress = {() => navigation.navigate('CreateGroup')}
      >
        <Text style = {styles.optionText}>Create Group</Text>
      </TouchableOpacity>    

    </View>
  );
};

export default Create_page

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: colors.lightBlue,
        justifyContent: 'center',
        alignItems: 'center',
        padding: 20,
    },
    title: {
        fontSize: 20,
        fontFamily: fonts.SemiBold,
        color: colors.primary,
        marginBottom: 40,
    },
    optionButton: {
        backgroundColor: colors.container,
        padding: 15,
        borderRadius: 10,
        marginVertical: 10,
        width: '80%',
        alignItems: 'center',
    },
    optionText: {
        fontSize: 16,
        fontFamily: fonts.SemiBold,
        color: colors.primary,
    },
})