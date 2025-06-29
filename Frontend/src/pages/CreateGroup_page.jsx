import { StyleSheet, Text, View, TextInput, FlatList, TouchableOpacity, Alert } from 'react-native';
import React, { useState } from 'react';
import { useNavigation } from '@react-navigation/native';
import axios from 'axios';
import { colors } from '../utils/colors';
import { fonts } from '../utils/fonts';
import { BASE_URL } from '../utils/config';
import AsyncStorage from '@react-native-async-storage/async-storage';

const API_PREFIX = 'https://when2meetimage-686579494898.asia-southeast1.run.app';

const CreateGroup_page = () => {
    const [groupName, setGroupName] = useState('');
    const [newMember, setNewMember] = useState('');
    const [members, setMembers] = useState([]);
    const navigation = useNavigation();

    const addMember = async () => {
        const trimmed = newMember.trim();
        if (!trimmed && members.includes(trimmed)) return;

        try {
            const token = await AsyncStorage.getItem('authToken');
            axios.defaults.headers.common['Authorization'] = `Token ${token}`;

            const res = await axios.get(`${API_PREFIX}${BASE_URL}/api/users/check/?email=${trimmed}`);
            if (res.data.exists) {
                setMembers([...members, trimmed]);
                setNewMember('');
            } else {
                Alert.alert("User not found", "The entered email does not match any registered user.");
            }
        } catch (err) {
            console.error(err);
            Alert.alert("Error", "Failed to check user existence")
        }
    };

    const removeMember = (email) => {
        Alert.alert(
            "Remove Member",
            `Remove ${email} from the group?`,
            [
                { text: "Cancel", style: "cancel" },
                { text: "Remove", style: "destructive", onPress: () => {
                    setMembers(members.filter(m => m !== email));
                    }
                }
            ]
        );
    };

    const handleCreateGroup = async () => {
        try {
            const token = await AsyncStorage.getItem('authToken');
            axios.defaults.headers.common['Authorization'] = `Token ${token}`;

            const response = await axios.post(
                `${API_PREFIX}${BASE_URL}/api/groups/`,
                {
                    name: groupName,
                    members: members,
                }
            );
            Alert.alert('Success', `Group created`);
            navigation.navigate('Main', {
                newGroup: {
                    ...response.data,
                    is_organiser: true,
                }
            });
        } catch (error) {
            console.error('Group creation failed:', error.response?.data || error.message);
            Alert.alert('Error', 'Failed to create group');
        }
    };


  return (
    <View style = {styles.container}>
        <View style = {styles.headerContainer}>
            <TouchableOpacity style = {styles.cancelContainer} onPress = {() => navigation.navigate('Main')}>
              <Text style = {styles.cancelText}>Cancel</Text>
            </TouchableOpacity>
            
            <Text style = {styles.headerText}>Create New Group</Text>
      
            <TouchableOpacity 
                onPress = {handleCreateGroup}
                style = {[styles.createButton, !(groupName && members.length) && { opacity: 0.5 }]}
                disabled = {!groupName || members.length === 0}>
                <Text style = {styles.createText}>New</Text>
            </TouchableOpacity>
        </View>

        <View style = {styles.groupContainer}>
            <TextInput
                style = {styles.input}
                placeholder = "Group Name"
                value = {groupName}
                onChangeText = {setGroupName}
            />

            <TextInput
                style = {styles.input}
                placeholder = "Add user email"
                value = {newMember}
                onChangeText = {setNewMember}
                onSubmitEditing={addMember}
            />

            <TouchableOpacity onPress = {addMember} style = {styles.addButton}>
                <Text style = {styles.addButtonText}> Add Member</Text>
            </TouchableOpacity>

            <FlatList
                data = {members}
                keyExtractor={(item) => item}
                renderItem={({ item }) => (
                    <TouchableOpacity onPress = {() => removeMember(item)}>
                        <Text style = {styles.member}>{item}</Text>
                    </TouchableOpacity>
                )}
                ListEmptyComponent={<Text style = {styles.member}>No members yet</Text>} 
            />

        </View>
    </View>
  )
}

export default CreateGroup_page

const styles = StyleSheet.create({
    container: {
        flex: 1,
        padding: 30,
        paddingTop: 100,
        backgroundColor: colors.white,
    },  
    
    headerContainer: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: 20,
    },

    cancelText: {
        color: 'red',
        fontFamily: fonts.Regular,
    },
    headerText: {
        fontSize: 20,
        fontFamily: fonts.SemiBold,
        color: colors.primary,
    },
    createText: {
        color: colors.primary,
        fontFamily: fonts.SemiBold,
    },
    input: {
        backgroundColor: colors.container,
        borderRadius: 10,
        padding: 15,
        marginBottom: 15,
    },
    addButton: {
        backgroundColor: colors.primary,
        padding: 12,
        borderRadius: 8,
        alignItems: 'center',
        marginBottom: 15,
    },
    addButtonText: {
        color: '#fff',
        fontFamily: fonts.Regular,
    },
    member: {
        paddingvertical: 6,
        fontFamily: fonts.Regular,
        color: colors.containerText,
    },
})