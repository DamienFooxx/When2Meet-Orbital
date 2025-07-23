import { StyleSheet, Text, View, TextInput, TouchableOpacity, Alert, ScrollView } from 'react-native';
import React, { useState } from 'react';
import { useUser } from '../context/UserContext';
import axios from 'axios';
import { API_BASE } from '../utils/config';
import { colors } from '../utils/colors';
import { fonts } from '../utils/fonts';
import Ionicons from 'react-native-vector-icons/Ionicons';
import { useNavigation, useRoute } from '@react-navigation/native';
import AsyncStorage from '@react-native-async-storage/async-storage';

const InviteUser_page = () => {
    const { user } = useUser();
    const { params } = useRoute();
    const navigation = useNavigation();
    const { group } = params || {};
    const [invited, setInvited] = useState([]);

    const [identifier, setIdentifier] = useState('');
    const [loading, setLoading] = useState(false);

    const addMember = async () => {
        const trimmed = identifier.trim();
        if (!trimmed || invited.includes(trimmed)) {
            return;
        }

        try {
            const token = await AsyncStorage.getItem('authToken');
            axios.defaults.headers.common['Authorization'] = `Token ${token}`;

            const res = await axios.get(`${API_BASE}/users/check/?email=${trimmed}`);
            if (res.data.exists) {
                setInvited([...invited, trimmed]);
                setIdentifier('');
            } else {
                Alert.alert("User not found", "The entered email does not match any registered user.");
            }
        } catch (err) {
            console.error(err);
            Alert.alert("Error", "Failed to check user existence");
        }
    };

    const removeMember = (email) => {
        Alert.alert(
            "Remove",
            `Remove ${email} from invite list?`,
            [
                { text: "Cancel", style: "cancel" },
                {
                text: "Remove", style: "destructive",
                onPress: () => setInvited(invited.filter(e => e !== email))
                }
            ]
            );
        };

    const sendInvites = async () => {
        if (invited.length === 0) {
            Alert.alert('No members', 'Add at least one member before sending invites');
            return;
        }

        try {
            const token = await AsyncStorage.getItem('authToken');
            axios.defaults.headers.common['Authorization'] = `Token ${token}`;

            const res = await axios.post(`${API_BASE}/groups/${group.id}/invite/`, {
                identifiers: invited,
            });

            Alert.alert('Success', res.data.message || 'Invites sent!');
            setInvited([]);
            navigation.goBack();
            } catch (err) {
            console.error('Invite failed:', err.response?.data || err.message);
            Alert.alert('Error', 'Failed to send invites.');
        }
    };

  return (
    <View style={styles.container}>
        {/* back button */}
        <TouchableOpacity onPress={() => navigation.goBack()} style={styles.backButton}>
            <Ionicons name="chevron-back" size={24} color={colors.primary} />
            <Text style={styles.backText}>Back</Text>
        </TouchableOpacity>

        <Text style={styles.title}>Invite to: {group?.name}</Text>
        
        <View style={styles.inputRow}>
            <TextInput
                style={styles.input}
                placeholder="Enter username or email"
                value={identifier}
                onChangeText={setIdentifier}
                autoCapitalize="none"
            />

            {/* add member */}
            <TouchableOpacity 
                style={styles.addButton} 
                onPress={addMember}
                disable={!identifier.trim()}
            >
                <Ionicons 
                    name="add-circle-outline" 
                    size={28} 
                    color={identifier.trim() ? colors.primary : colors.containerText} 
                />
            </TouchableOpacity>
        </View>

        {/* List of added members */}
        <ScrollView style={styles.invitedContainer}>
            {invited.length > 0 && (
            <>
                <Text style={styles.invitedHeader}>Members to be Invited:</Text>
                {invited.map((email, index) => (
                <View key={index} style={styles.invitedRow}>
                    <Text style={styles.invitedItem}>• {email}</Text>
                    <TouchableOpacity onPress={() => removeMember(email)}>
                    <Ionicons name="trash-outline" size={18} color="red" />
                    </TouchableOpacity>
                </View>
                ))}
            </>
            )}
        </ScrollView>
        {/* Send Invites button at bottom */}
        <TouchableOpacity style={styles.sendButton} onPress={sendInvites} disabled={loading}>
            <Text style={styles.sendText}>{loading ? 'Sending...' : 'Send Invites'}</Text>
        </TouchableOpacity>
    </View>
  );
};

export default InviteUser_page

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: colors.white,
        padding: 24,
        paddingTop: 80,
    },
    title: {
        fontSize: 22,
        fontFamily: fonts.SemiBold,
        marginBottom: 20,
        color: colors.primary,
    },
    inputRow: {
        flexDirection: 'row',
        alignItems: 'center',
        justifyContent: 'center',
        marginBottom: 16,
    },
    input: {
        flex: 1,
        borderWidth: 1,
        borderColor: colors.containerText,
        borderRadius: 10,
        padding: 12,
        fontFamily: fonts.Regular,
        height: 50,
        marginRight: 8,
    },
    addButton: {
        padding: 4,
        justifyContent: 'center',
        alignItems: 'center',
    },
    backButton: {
        flexDirection: 'row',
        alignItems: 'center',
        marginBottom: 20,
    },
    backText: {
        fontSize: 16,
        fontFamily: fonts.Medium,
        color: colors.primary,
        marginLeft: 6,
    },
    invitedContainer: {
        marginTop: 30,
            paddingTop: 10,
    borderTopWidth: 1,
    borderColor: colors.containerText,
    },
    invitedHeader: {
        fontFamily: fonts.SemiBold,
        fontSize: 16,
        marginBottom: 8,
        color: colors.primary,
    },
    invitedItem: {
        fontFamily: fonts.Regular,
        fontSize: 14,
        color: colors.darkBlue,
        marginBottom: 4,
    },
    invitedRow: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: 6,
    },
    sendButton: {
        backgroundColor: colors.primary,
        padding: 16,
        borderRadius: 8,
        alignItems: 'center',
        marginTop: 10,
        marginBottom: 12,
    },
    sendText: {
        color: 'white',
        fontFamily: fonts.SemiBold,
        fontSize: 16,
    },
})