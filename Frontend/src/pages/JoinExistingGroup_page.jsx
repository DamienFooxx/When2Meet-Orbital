import { StyleSheet, Text, View, FlatList, TouchableOpacity, Alert, TextInput, ActivityIndicator } from 'react-native';
import React, { useState } from 'react';
import axios from 'axios';
import { BASE_URL } from '../utils/config';
import { colors } from '../utils/colors';
import { fonts } from '../utils/fonts';
import { useUser } from '../context/UserContext';

const API_PREFIX = 'https://when2meetimage-686579494898.asia-southeast1.run.app';

const JoinExistingGroup_page = () => {
    const { user, isLoadingUser } = useUser();
    const [searchQuery, setSearchQuery] = useState('');
    const [filteredGroups, setFilteredGroups] = useState([]);
    const [loading, setLoading] = useState(false);
    const [confirmation, setConfirmation] = useState(null);

    // handle the search and filter groups
    const filterGroups = (text) => {
        setSearchQuery(text);
        if (!text.trim()) {
            setFilteredGroups([]);
            return;
        }

        setLoading(true);
        // fetch groups from the backend based on the search query (group code)
        axios.post(`${API_PREFIX}${BASE_URL}/api/groups/join-by-code/`, {
            invite_code: text,
        }, {
            headers: { Authorization: `Token ${user.token}` }
        })
        .then((response) => {
            setFilteredGroups([response.data.group_info]);
        })
        .catch((err) => {
            console.error(err);
            Alert.alert("Error", "Could not search for the group");
        })
        .finally(() => {
            setLoading(false);
        });
    };
    
    // send a join group request
    const requestToJoinGroup = async (groupCode, confirm = false) => {
        try {
            setLoading(true);
            const response = await axios.post(`${API_PREFIX}${BASE_URL}/api/groups/join-by-code/`, {
                invite_code: groupCode,
                confirm_join: true,
            }, {
                headers: { Authorization: `Token ${user.token}` }
            });
                Alert.alert("Success", response.data.message);

        } catch (err) {
            console.error("Join request failed", err);
            Alert.alert("Error", "Could not send join request");
        } finally {
            setLoading(false);
        }
    };

    const handleGroupSelection = (group) => {
        Alert.alert(
            `Confirm to join ${group.name}`,
            `Do you want to join the group "${group.name}"?`,
            [
                { text: 'Cancel', style: 'cancel'},
                { text: 'Confirm', onPress: () => requestToJoinGroup(group.invite_code) }
            ]
        );
    };

    const renderGroupItem = ({ item }) => (
        <View style={styles.card}>
            <Text style={styles.groupName}>{item.name}</Text>
            <Text style={styles.inviteCode}>Group Code: {item.invite_code}</Text>
            <TouchableOpacity
                style={styles.joinButton}
                onPress={() => handleGroupSelection(item)}
            >
                <Text style={styles.joinButtonText}>Join Group</Text>
            </TouchableOpacity>
        </View>
    )

    if (isLoadingUser || loading) {
        return (
            <View style={styles.loadingContainer}>
                <ActivityIndicator size="large" color={colors.lightBlue}/>
            </View>
        );
    }

  return (
    <View style={styles.container}>
        <Text style={styles.header}>Join an Existing Group</Text>

        {/* search bar */}
        <TextInput
            style={styles.searchInput}
            placeholder='Enter Group Code'
            value={searchQuery}
            onChangeText={filterGroups}
        />

        {/* display filtered results */}
        <FlatList
            data={filteredGroups}
            keyExtractor={(item) => item.invite_code.toString()}
            renderItem={renderGroupItem}
            ListEmptyComponent={<Text style={styles.noResults}>No groups found</Text>}
        />

    </View>
  )
}

export default JoinExistingGroup_page

const styles = StyleSheet.create({
    container: {
        flex: 1,
        padding: 20,
        paddingTop: 80,
        backgroundColor: colors.white,
    },
    header: {
        fontSize: 22,
        fontFamily: fonts.SemiBold,
        color: colors.primary,
        marginBottom: 20,
    },
    searchInput: {
        borderWidth: 1,
        borderColor: colors.containerText,
        borderRadius: 5,
        padding: 10,
        fontSize: 16,
        fontFamily: fonts.Regular,
        marginBottom: 20,
    },
    loadingContainer: {
        flex: 1,
        justifyContent: 'center',
        alignItems: 'center',
        backgroundColor: colors.white,
    },
    card: {
        backgroundColor: colors.lightBlue,
        padding: 15,
        borderRadius: 10,
        marginBottom: 10,
    },
    groupName: {
        fontSize: 18,
        fontFamily: fonts.SemiBold,
        marginBottom: 5,
        color: colors.primary,
    },
    inviteCode: {
        fontSize: 14,
        fontFamily: fonts.Regular,
        color: colors.containerText,
        marginBottom: 10,
    },
    joinButton: {
        backgroundColor: colors.primary,
        padding: 12,
        borderRadius: 10,
        alignItems: 'center',
    },
    joinButtonText: {
        color: colors.white,
        fontFamily: fonts.SemiBold,
        fontSize: 16,
    },
    noResults: {
        fontSize: 16,
        fontFamily: fonts.Medium,
        textAlign: 'center',
        marginTop: 40,
        color: colors.containerText,
    },
})