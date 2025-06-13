import { StyleSheet, Text, View, FlatList, TouchableOpacity, Alert, ActivityIndicator } from 'react-native'
import React, { useEffect, useState } from 'react'
import { useUser } from '../context/UserContext'
import axios from 'axios';
import { BASE_URL } from '../utils/config';
import { colors } from '../utils/colors';
import { fonts } from '../utils/fonts';
import { useNavigation } from '@react-navigation/native';
import Ionicons from 'react-native-vector-icons/Ionicons';

const Invitation_page = () => {
    const navigation = useNavigation();
    const { user, isLoadingUser } = useUser();
    const [invitations, setInvitations] = useState([]);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        if (!isLoadingUser && user?.token) {
            fetchInvitations();
        }
    }, [isLoadingUser, user]);

    const fetchInvitations = async () => {
        try {
            setLoading(true);
            const res = await axios.get(`${BASE_URL}/api/groups/invitations/`, {
                headers: { Authorization: `Token ${user.token}` }
            });
            setInvitations(res.data);
        } catch (err) {
            console.error("Failed to fetch invitations", err);
            Alert.alert("Error", "Could not load invitations");
        } finally {
            setLoading(false);
        }
    };

    const renderItem = ({ item }) => {
        <View style = {styles.card}>
            <Text style = {styles.groupName}>{item.name}</Text>
            <Text style = {styles.inviter}>Group Code: {item.invite_code}</Text>
        </View>
    };

    if (isLoadingUser || loading) {
        return (
            <View style={styles.loadingContainer}>
                <ActivityIndicator size = "large" color = {colors.lightBlue}/>
            </View>
        );
    }

  return (
    <View style = {styles.container}>
        <View style = {styles.topBar}>
            <TouchableOpacity onPress={() => navigation.navigate('Main')}>
                <Ionicons name="chevron-back-outline" size={24} color={colors.primary}/>
            </TouchableOpacity>
            <Text style = {styles.header}>Invitations</Text>
        </View>

        <FlatList
            data = {invitations}
            keyExtractor={(item) => item.id.toString()}
            renderItem={renderItem}
            ListEmptyComponent={<Text style={styles.noInvites}>No invitations</Text>}
        />
    </View>
  );
};

export default Invitation_page

const styles = StyleSheet.create({
    container: {
        flex: 1,
        padding: 20,
        paddingTop: 80,
        backgroundColor: colors.white,
    },
    topBar: {
        flexDirection: 'row',
        alignItems: 'center',
        marginBottom: 20,
        gap: 10,
    },
    loadingContainer: {
        flex: 1,
        justifyContent: 'center',
        alignItems: 'center',
        backgroundColor: colors.white,
    },
    header: {
        fontSize: 22,
        fontFamily: fonts.SemiBold,
        color: colors.primary,
    },
    noInvites: {
        fontSize: 16,
        fontFamily: fonts.Medium,
        textAlign: 'center',
        marginTop: 40,
        color: colors.containerText,
    },
    card: {
        backgroundColor: colors.lightBlue,
        padding: 15,
        borderRadius: 10, 
        marginBottom: 10,
    },
    groupName: {
        fontSize: 18,
        fontFamily: fonts.Semibold,
        marginBottom: 5,
        color: colors.primary,
    },
    inviter: {
        fontSize: 14,
        fontFamily: fonts.Regular,
        color: colors.containerText,
        marginBottom: 10,
    },
    actions: {
        color: 'green',
        fontfamily: fonts.Medium,
        fontSize: 14,
    },
    decline: {
        color: 'red',
        fontFamily: fonts.Medium,
        fontSize: 14,
    },
});