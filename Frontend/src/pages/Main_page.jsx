import { StyleSheet, Text, View, TouchableOpacity, TextInput, Modal } from 'react-native';
import React, {useState} from 'react';
import { colors } from '../utils/colors';
import { fonts } from '../utils/fonts';
import Ionicons from 'react-native-vector-icons/Ionicons';
import AntDesign from 'react-native-vector-icons/AntDesign';
import MaterialIcons from 'react-native-vector-icons/MaterialIcons';
import { useFocusEffect, useNavigation } from '@react-navigation/native';
import CreateEvent_page from './CreateEvent_page';

const Main_page = () => {
  const navigation = useNavigation();
  const route = useRoute();
  const [searchText, setSearchText] = useState('');
  const [upcomingEvents, setUpcomingEvents] = useState([]);

  const [invitations, setInvitations] = useState([]);

  {/* create event */}
  const [events, setEvents] = useState([]);
  const [modalVisible, setModalVisible] = useState(false);

  const handleAddEvent = (newEvent) => {
    setEvents(prev => [...prev, newEvent]);
    setModalVisible(false);
  }

  useFocusEffect(
    React.useCallback(() => {
        const { newGroup } = route.params || {};
        if (newGroup) {
            setUpcomingEvents((prev) => [...prev, newGroup]);
            navigation.setParams({ newGroup: null });
        }
    }, [route.params])
  );

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

      {upcomingEvents.length > 0 ? (
        upcomingEvents.map((event) => (
          <TouchableOpacity
            key = {event.id}
            style = {styles.event}
            onPress = {() => navigation.navigate('GroupDetail', { group: event })}
            >
            <Text style = {styles.eventTitle}>
              {event.title} {event.host ? '(Host)' : ''}
            </Text>
            <Text style = {styles.eventDetails}>
              {event.description || 'No description provided'}
            </Text>
            <Text style = {styles.eventDetails}>
              Date: {event.date || 'To be confirmed'}
            </Text>
            <Text style = {styles.eventDetails}>
              Participants: {event.participants?.join(', ') || 'None yet'}
            </Text>
          </TouchableOpacity>
        ))
      ) : (
        <View style = {styles.noEventContainer}>
        <Text style = {styles.noEventText}>No upcoming events</Text>
        </View>
      )}

      {/* invitations */}
      <View style = {styles.activitiesContainer}>
        <Text style = {styles.activitiesText}>Invitations</Text>
        <Ionicons name = "chevron-forward-circle" size = {25} color = {colors.primary}/>
      </View>

      {invitations.length > 0 ? (
        invitations.map((invite) => (
          <View key = {invite.id} style = {styles.invitationCard}>
            <Text style = {styles.invitationSender}>
              @{invite.sender} invites you to...
            </Text>
            <Text style = {styles.invitationEvent}>{invite.eventTitile}</Text>
          </View>
        ))
      ) : (
        <View style = {styles.noEventContainer}>
        <Text style = {styles.noEventText}>No invitations</Text>
        </View>
      )}

      <View style = {styles.bottomContainer}>
        {/* home */}
        <TouchableOpacity style = {styles.bottomButton}>
          <Ionicons name = "home-outline" size = {24} color = {'black'}/>
        </TouchableOpacity>

        {/* create group */}
        <TouchableOpacity style = {styles.bottomButton} onPress = {() => navigation.navigate('CreateGroup')}>
            <AntDesign name = "addusergroup" size = {24} color = {'black'}/>
        </TouchableOpacity>

        {/* create event */}
        <TouchableOpacity style = {styles.bottomButton} onPress = {() => setModalVisible(true)}>
          <MaterialIcons name = "event" size = {24} color = {'black'}/>
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
      
      <CreateEvent_page
        visible = {modalVisible}
        onClose = {() => setModalVisible(false)}
        onCreate = {handleAddEvent}
      />
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