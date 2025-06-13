import { StyleSheet, Text, View, Flatlist, TouchableOpacity, Alert, ActivityIndicator } from 'react-native'
import React, { useEffect, useState } from 'react'
import { useUser } from '../context/UserContext'
import axios from 'axios';
import { BASE_URL } from '../utils/config';
import { colors } from '../utils/colors';
import { fonts } from '../utils/fonts';

const Invitation_page = () => {
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
            const res = await axios.get(`${BASE_URL}/groups/invitations/`, {
                headers: { Authorization: `Bearer ${user.token}` }
            });
            setInvitations(res.data);
        } catch (err) {
            console.error("Failed to fetch invitations", err);
            Alert.alert("Error", "Could not load invitations");
        } finally {
            setLoading(false);
        }
    };

    const handleResponse = async (inviteId, action) => {
        try {
            await axios.post(`${BASE_URL}/groups/invitations/${inviteId}/${action}/`, {}, {
                headers: { Authorization: `Bearer ${user.token}`}
            });
            setInvitations(prev => prev.filter(invite => invite.id !== inviteId));
        } catch (err) {
            console.error(`Failed to ${action} invitation`, err);
            Alert.alert("Error", `Could not ${action} invitation`);
        }
    };

    const renderiTem = ({ item }) => {
        <View style = {styles.card}>
            <Text style = {styles.groupName}>{item.group_name}</Text>
            <Text style = {styles.inviter}>Invited by: {item.inviter_name}</Text>
            <View style = {styles.actions}>
                <TouchableOpacity onPress={() => handleResponse(item.id, 'accept')}>
                    <Text style = {styles.accept}>Accept</Text>
                </TouchableOpacity>
                <TouchableOpacity onPress={() => handleResponse(item.id, 'decline')}>
                    <Text style = {styles.decline}>Decline</Text>
                </TouchableOpacity>
            </View>
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
        <Text style = {styles.header}>Invitations</Text>
        <Flatlist
            data = {invitations}
            keyExtractor={item => item.id.toString()}
            renderiTem={renderiTem}
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
        paddingTop: 60,
        backgroundColor: colors.white,
    },
    loadingContainer: {
        flex: 1,
        justifyContent: 'center',
        alignItems: 'center',
        backgroundColor: colors.white,
    },
    header: {
        fontSize: 22,
        fontFamily: fonts.Medium,
        marginBottom: 20,
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