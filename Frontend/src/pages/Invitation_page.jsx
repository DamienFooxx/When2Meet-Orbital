import { StyleSheet, Text, View, FlatList, TouchableOpacity, Alert, ActivityIndicator, TextInput } from 'react-native';
import React, { useCallback, useState} from 'react';
import { useFocusEffect } from '@react-navigation/native';
import { useUser } from '../context/UserContext';
import { useRoute } from '@react-navigation/native';
import axios from 'axios';
import { API_BASE } from '../utils/config';
import { colors } from '../utils/colors';
import { fonts } from '../utils/fonts';
import { useNavigation } from '@react-navigation/native';
import Ionicons from 'react-native-vector-icons/Ionicons';

const Invitation_page = () => {
    const navigation = useNavigation();
    const { user, isLoadingUser } = useUser();
    const [invitations, setInvitations] = useState([]);
    const [requests, setRequests] = useState([]);
    const [loading, setLoading] = useState(false);
    const { params } = useRoute();

    useFocusEffect(
        useCallback(() => {
            if (!isLoadingUser && user?.token) {
                fetchInvitations();
                fetchRequests();
            }
        }, [isLoadingUser, user])
    );

    // fetch group invitations for user
    const fetchInvitations = async () => {
        try {
            setLoading(true);
            const res = await axios.get(`${API_BASE}/groups/invitations/`, {
                headers: { Authorization: `Token ${user.token}` }
            });
            setInvitations(res.data);

        } catch (err) {
            Alert.alert("Error", "Could not load invitations");
        } finally {
            setLoading(false);
        }
    };

    // fetch join requests for the organizer
    const fetchRequests = async () => {
        try { 
            setLoading(true);
            const res = await axios.get(`${API_BASE}/groups/requests/`, {
                headers: { Authorization: `Token ${user.token}` }
            });
            setRequests(res.data);
        } finally {
            setLoading(false);
        }
    };

    // accept a pending request
    const acceptRequest = async (requestId) => {
        try {
            await axios.post(`${API_BASE}/groups/requests/${requestId}/accept-request/`, {}, {
                headers: { Authorization: `Token ${user.token}` }
            });
            fetchRequests();
            Alert.alert("Success", "You have accepted the join request")
        } catch (err) {
            console.error("Accept failed", err);
            Alert.alert("Error", "Could not accept the request");
        }
    };

    // decline a pending request
    const declineRequest = async (requestId) => {
        try {
            await axios.post(`${API_BASE}/groups/requests/${requestId}/decline-request/`, {}, {
                headers: { Authorization: `Token ${user.token}` }
            });
            fetchRequests(); // refresh request list
        } catch (err) {
            console.error("Deline failed", err);
            Alert.alert("Error", "Could not decline the request.")
        }
    }

    // accept a pending invitation
    const acceptInvitation = async (groupId) => {
        try {
            await axios.post(`${API_BASE}/groups/${groupId}/accept-invitation/`, {}, {
                headers: { Authorization: `Token ${user.token}` }
            });

            fetchInvitations(); // refresh list

            Alert.alert("Success", "You have joined the group")
        } catch (err) {
            console.error("Accept failed", err);
            Alert.alert("Error", "Could not accept invitation.");
        }
        };

    const declineInvitation = async (groupId) => {
        try {
            await axios.post(`${API_BASE}/groups/${groupId}/decline-invitation/`, {}, {
            headers: { Authorization: `Token ${user.token}` }
            });
            fetchInvitations(); // Refresh list
        } catch (err) {
            console.error("Decline failed", err);
            Alert.alert("Error", "Could not decline invitation.");
        }
        };

    const renderInviteItem = ({ item }) => (
        <View style = {styles.card}>
            <Text style = {styles.groupName}>{item.name}</Text>
            <Text style = {styles.inviter}>Group Code: {item.invite_code}</Text>
            <View style={{ flexDirection: 'row', gap: 20 }}>
                <TouchableOpacity onPress={() => acceptInvitation(item.id)}>
                    <Text style={styles.actions}>Accept</Text>
                </TouchableOpacity>
                <TouchableOpacity onPress={() => {
                    Alert.alert(
                        "Confirm Decline",
                        "Are you sure you want to decline this invitation?",
                        [
                            { text: "Cancel", style: "cancel"},
                            { text: "Yes", onPress: () => declineInvitation(item.id) }
                        ]
                    );
                }}>
                    <Text style = {styles.decline}>Decline</Text>
                </TouchableOpacity>
            </View>
        </View>
    );

    // Render the requests list (only for the organizer)
    const renderRequestItem = ({ item }) => (
        <View style={styles.card}>
            <Text style={styles.groupName}>User: {item.user.name}</Text>
            <Text style={styles.inviter}>Email: {item.user.email}</Text>
            <Text style={styles.inviter}>Group: {item.group.name}</Text>
            <View style={{ flexDirection: 'row', gap: 20 }}>
                <TouchableOpacity onPress={() => acceptRequest(item.id)}>
                    <Text style={styles.actions}>Accept</Text>
                </TouchableOpacity>
                <TouchableOpacity onPress={() => {
                    Alert.alert(
                        "Confirm Decline",
                        "Are you sure you want to decline this request?",
                        [
                            { text: "Cancel", style: "cancel" },
                            { text: "Yes", onPress: () => declineRequest(item.id) }
                        ]
                    );
                }}>
                    <Text style={styles.decline}>Decline</Text>
                </TouchableOpacity>
            </View>
        </View>
    );

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

        {/* button to navigate to the 'JoinExistingGroup_page' */}
        <TouchableOpacity
            style={styles.joinButton}
            onPress={() => navigation.navigate('JoinExistingGroup')}
        >
            <Text style={styles.joinButtonText}>Join an Existing Group</Text>
        </TouchableOpacity>


        
        {/* invitations list */}
        <Text style={styles.invites}>Invites</Text>
        <FlatList
            data = {invitations}
            keyExtractor={(item) => item.id.toString()}
            renderItem={renderInviteItem}
            ListEmptyComponent={<Text style={styles.noInvites}>No invitations</Text>}
        />

        {/* requests list */}
        <Text style={styles.invites}>Requests</Text>
        <FlatList
            data = {requests}
            keyExtractor={(item) => item.id.toString()}
            renderItem={renderRequestItem}
            ListEmptyComponent={<Text style={styles.noInvites}>No requests</Text>}
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
    invites: {
        fontSize: 20,
        fontFamily: fonts.SemiBold,
        color: colors.primary,
        paddingTop: 25,
    },
    inviter: {
        fontSize: 14,
        fontFamily: fonts.Regular,
        color: colors.containerText,
        marginBottom: 10,
    },
    actions: {
        color: 'green',
        fontFamily: fonts.Medium,
        fontSize: 14,
    },
    decline: {
        color: 'red',
        fontFamily: fonts.Medium,
        fontSize: 14,
    },
    joinButton: {
        backgroundColor: colors.primary,
        padding: 15,
        borderRadius: 10,
        marginTop: 20,
        alignItems: 'center',
    },
    joinButtonText: {
        color: colors.white,
        fontFamily: fonts.SemiBold,
        fontSize: 16,
    },
});