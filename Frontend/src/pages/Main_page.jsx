import { StyleSheet, Text, View, TouchableOpacity, TextInput, Alert } from 'react-native';
import React, {useState, useEffect} from 'react';
import { colors } from '../utils/colors';
import { fonts } from '../utils/fonts';
import Ionicons from 'react-native-vector-icons/Ionicons';
import { useFocusEffect, useNavigation, useRoute } from '@react-navigation/native';
import axios from 'axios';
import { BASE_URL, API_PREFIX } from '../utils/config';
import { useUser } from '../context/UserContext';
import Clipboard from '@react-native-clipboard/clipboard';
import AsyncStorage from '@react-native-async-storage/async-storage';

const Main_page = () => {
  const navigation = useNavigation();
  const route = useRoute();
  const [searchText, setSearchText] = useState('');
  const [groups, setGroups] = useState([]);
  const { user } = useUser();

  // create event
  const [events, setEvents] = useState([]);

  const handleAddEvent = (newEvent) => {
    setEvents(prev => [...prev, newEvent]);
    setModalVisible(false);
  }

  // retrieve created groups
  const fetchGroups = async () => {
    try {
        const token = await AsyncStorage.getItem('authToken');  // Retrieve the token from AsyncStorage

        // Set the token in the Axios headers
        axios.defaults.headers.common['Authorization'] = `Token ${token}`;

        // GET request to fetch groups
        const res = await axios.get(`${API_PREFIX}${BASE_URL}/groups/`);

        // check if there is an array of groups
        if (!Array.isArray(res.data)) {
            console.error("Invalid response data:", res.data);
            return;
        }
        // filter groups to show only accepted members
        const updatedGroups = res.data.map(group => ({
            ...group,
            members: Array.isArray(group.members) ? group.members.filter(member => member.is_accepted) : [],
        }));

        // if no groups found
        if (updatedGroups.legnth === 0) {
            console.log("No groups available.");
        } else {
            console.log("fetched and updated groups:", updatedGroups)
        }
        setGroups(updatedGroups);
    } catch (error) {
            console.error("Error fetching groups:", error.response);
    if (error.response) {
        console.log("Error Data:", error.response.data);  // More detailed error
        console.log("Error Code:", error.response.status);
        Alert.alert("Error", `Error Code: ${error.response.status} - ${error.response.data.detail}`);
    } else if (error.request) {
        console.log("No response received:", error.request);
        Alert.alert("Error", "No response from server.");
    } else {
        console.log("Request failed:", error.message);
        Alert.alert("Error", `Request failed: ${error.message}`);
    }
    }
  };

  // delete event
    const confirmDeleteGroup = (groupId) => {
    Alert.alert(
        'Delete Group',
        'Are you sure you want to delete this group',
        [
            { text: 'Cancel', style: 'cancel' },
            { text: 'Delete', style: 'destructive', onPress: () => handleDelete(groupId) }
        ]
    );
  };

  const handleDelete = async (groupId) => {
    try {
        // cretes a HTTP delete request
        await axios.delete(`${API_PREFIX}${BASE_URL}/groups/${groupId}/`, {
            headers: { Authorization: `Token ${user.token}` },
        });
        Alert.alert('Deleted', 'Group has been deleted');
        fetchGroups(); // refresh list after deletion
    } catch (err) {
        console.error('Failed to delete group:', err);
        Alet.alert('Error', 'Could not delete group.');
    }
  };

  // call created group/event
  useFocusEffect(
    React.useCallback(() => {
        fetchGroups();  // fetch backend data

        const { newGroup, newEvent } = route.params || {};

        if (newGroup) {
            setGroups((prev) => [newGroup, ...prev]);
            navigation.setParams({ newGroup: null });
        }

        if (newEvent) {
            setEvents(prev => [newEvent, ...prev]);
            navigation.setParams({ newEvent: null});
        }

        return () => {};
    }, [route.params])
  );

  useEffect(() => {
    navigation.setParams({ fetchGroups });
  }, []);


  return (
    <View style = {styles.container}>

      {/* search button */}
      <View style = {styles.searchcontainer}>
        <Ionicons
        name = {'search'}
        color = {colors.containerText}
        size = {25}
        />
        <TextInput style = {styles.searchText}
        placeholder = 'Search'
        placeholderTextColor = {colors.containerText}
        value = {searchText}
        onChangeText = {setSearchText}
        />
      </View>

      <View style = {styles.buttonRow}>
        <TouchableOpacity style = {styles.iconButton}>
          <Ionicons name = 'heart-outline' size = {18} color = {colors.primary} />
          <Text style = {styles.iconButtonText}>Favorites</Text>
        </TouchableOpacity>

        <TouchableOpacity style = {styles.iconButton}>
          <Ionicons name = 'time-outline' size = {18} color = {colors.primary} />
          <Text style = {styles.iconButtonText}>History</Text>
        </TouchableOpacity>
      </View>

      {/* upcoming activities */}
      <View style = {styles.activitiesContainer}>
        <Text style = {styles.activitiesText}>Upcoming Activities</Text>
        <Ionicons name = "chevron-forward-circle" size = {25} color = {colors.primary}/>
      </View>

      {events.length > 0 ? (
        events.map((event, index) => (
            <TouchableOpacity
                key = {index}
                style = {styles.eventCard}
                onPress = {() => navigation.navigate('EventDetail', { event })}
            >
                <Text style = {styles.eventTitle}>{event.title}</Text>
                <Text style = {styles.eventDetails}>{event.description || 'No description provided'}</Text>
                <Text style = {styles.eventDetails}>Mode: {event.mode || 'Not set'}</Text>
                <Text style = {styles.eventDetails}>Duration: {event.duration || 'Not set'}</Text>
            </TouchableOpacity>
        ))
      ) : (
        <View style = {styles.noEventContainer}>
            <Text style = {styles.noEventText}>No events yet</Text>
        </View>
      )}

      {/* groups */}
      <View style = {styles.activitiesContainer}>
        <Text style = {styles.activitiesText}>Groups</Text>
        <Ionicons name = "chevron-forward-circle" size = {25} color = {colors.primary}/>
      </View>

      {groups.length > 0 ? (
        groups.map((group, index) => (
          <View key = {index} style = {styles.groupCardWrapper}>
            <TouchableOpacity
                key={index}
                style={styles.groupCard}
                onPress={() => navigation.navigate('GroupDetail', { group })}
                >
                <View style={{ flexDirection: 'row', justifyContent: 'center' }}>
                    <View style={{ flex: 1}}>
                        <Text style={styles.groupName}>
                        {group.name || group.title} {group.is_organiser ? '(Organiser)' : ''}
                        </Text>
                </View>
                    {/* COPY LINK ICON */}
                    <TouchableOpacity
                        onPress = {() => {
                            Clipboard.setString(group.invite_code);
                            Alert.alert('Copied', 'Group code copied to clipboard');
                        }}
                        style = {{ marginHorizontal: 8}}
                    >
                        <Ionicons name = 'link-outline' size = {20} color = {colors.containerText}/>
                    </TouchableOpacity>

                    {/* DELETE BUTTON */}
                    {group.is_organiser && (
                    <TouchableOpacity onPress={() => confirmDeleteGroup(group.id)}>
                        <Ionicons name="trash-outline" size={20} color="red" />
                    </TouchableOpacity>
                    )}

                    
                </View>

            </TouchableOpacity>
          </View>
        ))
      ) : (
        <View style = {styles.noEventContainer}>
        <Text style = {styles.noEventText}>No groups yet</Text>
        </View>
      )}

    
      <View style = {styles.bottomContainer}>
        {/* home */}
        <TouchableOpacity style = {styles.bottomButton}>
          <Ionicons name = "home-outline" size = {24} color = {'black'}/>
        </TouchableOpacity>

        {/* invitations */}
        <TouchableOpacity style = {styles.bottomButton} onPress = {() => navigation.navigate('Invitation')}>
            <Ionicons name = "mail-unread" size = {24} color = {'black'}/>
        </TouchableOpacity>

        {/* create event/group */}
        <TouchableOpacity style = {styles.bottomButton} onPress = {() => navigation.navigate('Create')}>
          <Ionicons name = "add-circle" size = {24} color = {'black'}/>
        </TouchableOpacity>
        
        {/* calendar */}
        <TouchableOpacity style = {styles.bottomButton} onPress = {() => navigation.navigate('Calendar')}>
            <Ionicons name = "calendar-number" size = {24} color = {'black'}/>
        </TouchableOpacity>
        
        {/* profile */}
        <TouchableOpacity style = {styles.bottomButton} onPress = {() => navigation.navigate('Profile')}>
          <Ionicons name = "person-outline" size = {24} color = {'black'}/>
        </TouchableOpacity>

      </View>
      
    </View>
  )
}

export default Main_page

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.lightBlue,
    padding: 30,
  },

  searchcontainer: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#F5F5F5',
    borderColor: '#F5F5F5',
    borderRadius: 5,
    height: 45,
    marginTop: 40,
    borderWidth: 1,
    padding: 10,
    paddingHorizontal: 20,
  },

  searchText: {
    marginLeft: 10,
    flex: 1,
    fontFamily: fonts.Regular,
  },

  buttonRow: {
    flexDirection: 'row',
    gap: 5,
    marginTop: 10,
  },

  iconButton: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: colors.container,
    paddingVertical: 8,
    paddingHorizontal: 12,
    borderRadius: 8,
    borderColor: colors.container,
    borderWidth: 1,
  },

  iconButtonText: {
    marginLeft: 6,
    fontFamily: fonts.Regular,
    color: 'black',
    fontSize: 14,
  },

  activitiesContainer: {
    flexDirection: 'row',
    marginTop: 20,
    marginBottom: 20,
    alignItems: 'left',
  },

  activitiesText: {
    fontSize: 18,
    fontFamily: fonts.SemiBold,
    marginHorizontal: 4,
  },

  eventCard: {
    backgroundColor: colors.container,
    borderRadius: 10,
    padding: 15,
    marginBottom: 10,
  },

  eventTitle: {
    fontFamily: fonts.SemiBold,
    fontSize: 15,
    color: colors.primary,
  },
  eventDetails: {
    fontFamily: fonts.Regular,
    fontSize: 13,
    color: colors.primary,
  },

  noEventContainer: {
    alignItems: 'center',
    marginTop: 20,
    marginBottom: 60
  },

  noEventText: {
    fontFamily: fonts.Regular,
    fontSize: 14,
    color: colors.primary,
    marginTop: 5,
  },

  invitationCard: {
    backgroundColor: colors.container,
    borderRadius: 10,
    padding: 15,
    marginBottom: 10,
  },

  invitationSender: {
    fontFamily: fonts.SemiBold,
    fontSize: 14,
    color: colors.primary,
  },

  invitationEvent: {
    fontFamily: fonts.Regular,
    fontSize: 14,
    color: colors.primary,
  },
  groupCardWrapper:{
    position: 'relative',
  },
  deleteButton: {
    position: 'absolute',
    top: 10,
    right: 10,
    zIndex: 1,
  },
  groupCard: {
    backgroundColor: colors.container,
    borderRadius: 10,
    padding: 15,
    marginBottom: 10,
  },
  groupName: {
    fontFamily: fonts.SemiBold,
    fontSize: 15,
    color: colors.primary,
  },
  groupMembers: {
    fontFamily: fonts.Regular,
    fontSize: 13,
    color: colors.primary,
  },
  bottomContainer: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    alignItems: 'center',
    height: 85,
    paddingBottom: 15,
    backgroundColor: 'white',
    position: 'absolute',
    bottom: 0,
    left: 0,
    right: 0,
  },
})