import { StyleSheet, Text, View, ScrollView } from 'react-native';
import React from 'react';
import { useRoute } from '@react-navigation/native';
import { colors } from '../utils/colors';
import { fonts } from '../utils/fonts';

const GroupDetail_page = () => {
    const { params } = useRoute()
    const { group } = params || {}

    if (!group) {
        return (
            <View style = {styles.container}>
                <Text style = {styles.title}>No group data found.</Text>
            </View>
        )
    }

  return (
    <ScrollView contentContainerStyle = {styles.container}>
      <Text style = {styles.title}>{group.title}</Text>
      <Text style = {styles.sectionHeader}>Participants:</Text>
      {group.participants?.length > 0 ? (
        group.participants.map((email, idx) => (
            <Text key = {idx} style = {styles.participant}>{email}</Text>
        ))
      ) : (
        <Text style = {styles.participant}>No participants listed.</Text>
      )}
      <Text style = {styles.sectionHeader}>Date:</Text>
      <Text style = {styles.participant}>{group.date || 'To be confirmed'}</Text>
    </ScrollView>
  )
}

export default GroupDetail_page

const styles = StyleSheet.create({
    container: {
        flexGrow: 1,
        padding: 24,
        paddingTop: 80,
        backgroundColor: colors.brownBackground,
    },

    title: {
        fontSize: 24,
        fontFamily: fonts.SemiBold,
        color: colors.primary,
        marginBottom: 8,
    },
    sectionHeader: {
        fontSize: 18,
        fontFamily: fonts.SemiBold,
        marginTop: 16,
        marginBottom: 6,
        color: colors.primary,
    },
    participant: {
        fontSize: 15,
        fontFamily: fonts.Regular,
        color: colors.containerText,
        marginBottom: 4,
    },

})