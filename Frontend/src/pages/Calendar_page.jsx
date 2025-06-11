import { StyleSheet, Text, View, TouchableOpacity } from 'react-native'
import React, { useEffect, useState } from 'react'
import AntDesign from 'react-native-vector-icons/AntDesign';
import { useNavigation } from '@react-navigation/native';
import { colors } from '../utils/colors';
import { fonts } from '../utils/fonts';

const Calendar_page = () => {
    const [view, setView]  = useState("month")
  return (
    <View>
      <Text>Calendar_page</Text>
    </View>
  )
}

export default Calendar_page

const styles = StyleSheet.create({})