import { StyleSheet, Text, View, ScrollView, ActivityIndicator } from 'react-native';
import React, { useState, useEffect } from 'react';
import { useRoute } from '@react-navigation/native';
import { useUser } from '../context/UserContext';
import { colors } from '../utils/colors';
import { fonts } from '../utils/fonts';
import { BASE_URL } from '../utils/config';
import axios from 'axios';

const GroupDetail_page = () => {
    const { params } = useRoute();
    const { group } = params || {};
    const [members, setMembers] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const { user } = useUser();
    const [ groupDetails, setGroupDetails] = useState(null);

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
        <Text style={styles.title}>{group.name}</Text>
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
        color: colors.darkBlue,
        marginBottom: 4,
    },
    participantStatus: {
        fontSize: 13,
        fontFamily: fonts.Regular,
        color: colors.containerText,
    }

})