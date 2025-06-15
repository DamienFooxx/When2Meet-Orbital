import { StyleSheet, Text, View, ScrollView, ActivityIndicator, TouchableOpacity } from 'react-native';
import React, { useState, useEffect } from 'react';
import { useNavigation, useRoute } from '@react-navigation/native';
import { useUser } from '../context/UserContext';
import { colors } from '../utils/colors';
import { fonts } from '../utils/fonts';
import { BASE_URL } from '../utils/config';
import { Alert } from 'react-native';
import axios from 'axios';
import Ionicons from 'react-native-vector-icons/Ionicons';

const GroupDetail_page = () => {
    const { params } = useRoute();
    const { group } = params || {};
    const [members, setMembers] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const { user } = useUser();
    const [ groupDetails, setGroupDetails] = useState(null);
    const navigation = useNavigation();

    if (!group) {
        return (
            <View style = {styles.container}>
                <Text style = {styles.title}>No group data found.</Text>
            </View>
        )
    }

    // fetch members
    useEffect(() => {
        if (!group.id) return; 

        const fetchData = async () => {
            try {
                // Fetch group details
                const groupRes = await axios.get(`${BASE_URL}/api/groups/${group.id}/`, {
                    headers: { Authorization: `Token ${user.token}` }
                });
                setGroupDetails(groupRes.data);

                // Fetch group members
                const membersRes = await axios.get(`${BASE_URL}/api/groups/${group.id}/members/`, {
                    headers: { Authorization: `Token ${user.token}` }, // ensure authentication
                });
                setMembers(membersRes.data);

                setLoading(false);
            } catch (err) {
                console.error('Failed to fetch members:', err);
                setError('Could not fetch members');
                setLoading(false);
            }
        };
        fetchData();
    }, [group.id, user.token]); // fetch members whenever the group ID or user token changes
    
    // leave group
    const leaveGroup = async () => {
        Alert.alert(
            'Leave group',
            'Are you sure you want to leave this group?',
            [
                { text: 'Cancel', style: 'cancel'},
                {
                    text: 'Leave',
                    style: 'destructive',
                    onPress: async() => {
                        try {
                            const res = await axios.post(`${BASE_URL}/api/groups/${group.id}/leave/`, {}, {
                                headers: { Authorization: `Token ${user.token}` },
                            });
                            Alert.alert("Left group", "You have left the group.");
                            navigation.goBack();
                        } catch (err) {
                            const message = err.response?.data?.detail || 'Could not leave group'
                            Alert.alert('Error', message)
                        }
                    }
                }
            ]
        );
    };

    // handle loading state
    if (loading || !groupDetails) {
        return (
            <View style = {styles.container}>
                <ActivityIndicator size='large' color={colors.primary}/>
            </View>
        );
    }

    // handle error state
    if (error) {
        return (
            <View style = {styles.container}>
                <Text style = {styles.title}>{error}</Text>
            </View>
        )
    }
  

    return (
    <ScrollView contentContainerStyle = {styles.container}>
        <View style={{ flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center'}}>
        {/* group name */}
        <Text style={styles.title}>{group.name}</Text>

        {/* leave group */}
        {groupDetails?.is_organiser !== true && (
            <TouchableOpacity onPress={leaveGroup}>
                <Ionicons name='log-out-outline' size={24} color={colors.containerText}/>
            </TouchableOpacity>
        )}
        </View>
        
        {/* group code */}
        <Text style={styles.groupCodeLabel}>Group Code:</Text>
        <Text style={styles.groupCode}>{groupDetails.invite_code}</Text>
        
        {/* participants */}
        <Text style={styles.sectionHeader}>Participants:</Text>

        {/* Display members */}
        {members.length > 0 ? (
            members.map((member, idx) => (
                <View 
                    key={member?.profile?.id || idx} 
                    style={styles.participantContainer}
                >
                    <Text style={[
                        styles.participant,
                        member.role === 'organiser' && styles.organiserText
                    ]}>
                        {member.role === 'organiser' ? `${member?.profile?.username}` : member?.profile?.username || 'Unknown'}
                    </Text>
                    {member.role !== 'organiser' && (
                        <Text style={styles.participantStatus}>
                            Status: {member.is_accepted ? 'Accepted' : 'Pending'}
                        </Text>
                    )}
                    
                </View>
            ))
        ) : (
            <Text style={styles.participant}>No participants listed.</Text>
        )}
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
    participantContainer: {
        backgroundColor: colors.greyBlue,
        padding: 16,
        borderRadius: 8,
        marginBottom: 6,
    },
    title: {
        fontSize: 24,
        fontFamily: fonts.SemiBold,
        color: colors.primary,
        marginBottom: 8,
    },
    groupCodeLabel: {
        fontSize: 14, 
        fontFamily: fonts.SemiBold,
        color: colors.primary,
        marginTop: 4,
    },
    groupCode: {
        fontSize: 20,
        fontFamily: fonts.Light,
        color: colors.primary,
        marginBottom: 12,
    },
    sectionHeader: {
        fontSize: 18,
        fontFamily: fonts.SemiBold,
        marginTop: 16,
        marginBottom: 6,
        color: colors.primary,
    },
    organiserText: {
        fontFamily: fonts.SemiBold,
        color: colors.darkBlue,
    },
    participant: {
        fontSize: 15,
        fontFamily: fonts.SemiBold,
        color: colors.prima,
        marginBottom: 4,
    },
    participantStatus: {
        fontSize: 13,
        fontFamily: fonts.Regular,
        color: colors.containerText,
    }

})