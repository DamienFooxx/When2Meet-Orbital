import { StyleSheet, Text, View, ScrollView, ActivityIndicator, TouchableOpacity, Alert } from 'react-native';
import React, { useState, useEffect } from 'react';
import { useNavigation, useRoute } from '@react-navigation/native';
import { useUser } from '../context/UserContext';
import { colors } from '../utils/colors';
import { fonts } from '../utils/fonts';
import { API_BASE } from '../utils/config';
import axios from 'axios';
import Ionicons from 'react-native-vector-icons/Ionicons';

const EventDetail_page = () => {
    const { params } = useRoute();
    const { event } = params || {};
    const [eventDetails, setEventDetails] = useState(null);
    const [participants, setParticipants] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const { user } = useUser();
    const navigation = useNavigation();

    if (!event) {
        return (
            <View style={styles.container}>
                <Text style={styles.title}>No event data found.</Text>
            </View>
        );
    }

    // Fetch event details and participants
    useEffect(() => {
        if (!event.id) return;

        const fetchEventData = async () => {
            try {
                // Fetch event details
                const eventRes = await axios.get(`${API_BASE}/events/${event.id}/`, {
                    headers: { Authorization: `Token ${user.token}` }
                });
                setEventDetails(eventRes.data);

                // Fetch event participants
                const participantsRes = await axios.get(`${API_BASE}/events/${event.id}/participants/`, {
                    headers: { Authorization: `Token ${user.token}` }
                });
                setParticipants(participantsRes.data);

                setLoading(false);
            } catch (err) {
                console.error('Failed to fetch event data:', err);
                setError('Could not fetch event details');
                setLoading(false);
            }
        };

        fetchEventData();
    }, [event.id, user.token]);

    // Join event
    const joinEvent = async () => {
        try {
            await axios.post(`${API_BASE}/events/${event.id}/join/`, {}, {
                headers: { Authorization: `Token ${user.token}` }
            });
            Alert.alert('Success', 'You have joined the event!');
            // Refresh participants list
            const participantsRes = await axios.get(`${API_BASE}/events/${event.id}/participants/`, {
                headers: { Authorization: `Token ${user.token}` }
            });
            setParticipants(participantsRes.data);
        } catch (err) {
            const message = err.response?.data?.detail || 'Could not join event';
            Alert.alert('Error', message);
        }
    };

    // Leave event
    const leaveEvent = async () => {
        Alert.alert(
            'Leave Event',
            'Are you sure you want to leave this event?',
            [
                { text: 'Cancel', style: 'cancel' },
                {
                    text: 'Leave',
                    style: 'destructive',
                    onPress: async () => {
                        try {
                            await axios.post(`${API_BASE}/events/${event.id}/leave/`, {}, {
                                headers: { Authorization: `Token ${user.token}` }
                            });
                            Alert.alert('Success', 'You have left the event.');
                            navigation.goBack();
                        } catch (err) {
                            const message = err.response?.data?.detail || 'Could not leave event';
                            Alert.alert('Error', message);
                        }
                    }
                }
            ]
        );
    };

    // Edit event (for organizers)
    const editEvent = () => {
        navigation.navigate('EditEvent', { event: eventDetails });
    };

    // Delete event (for organizers)
    const deleteEvent = async () => {
        Alert.alert(
            'Delete Event',
            'Are you sure you want to delete this event? This action cannot be undone.',
            [
                { text: 'Cancel', style: 'cancel' },
                {
                    text: 'Delete',
                    style: 'destructive',
                    onPress: async () => {
                        try {
                            await axios.delete(`${API_BASE}/events/${event.id}/`, {
                                headers: { Authorization: `Token ${user.token}` }
                            });
                            Alert.alert('Success', 'Event has been deleted.');
                            navigation.goBack();
                        } catch (err) {
                            const message = err.response?.data?.detail || 'Could not delete event';
                            Alert.alert('Error', message);
                        }
                    }
                }
            ]
        );
    };

    // Format date and time
    const formatDateTime = (dateTimeString) => {
        if (!dateTimeString) return 'Not specified';
        const date = new Date(dateTimeString);
        return date.toLocaleString();
    };

    // Check if current user is the organizer
    const isOrganizer = eventDetails?.organizer?.id === user?.id;

    // Check if current user is a participant
    const isParticipant = participants.some(p => p.user?.id === user?.id);

    // Start availability collection (for organizers)
    const startAvailabilityCollection = async () => {
        try {
            await axios.post(`${API_BASE}/events/${event.id}/start-availability-collection/`, {}, {
                headers: { Authorization: `Token ${user.token}` }
            });
            Alert.alert('Success', 'Availability collection has started! Participants can now submit their availability.');
            // Refresh event details
            const eventRes = await axios.get(`${API_BASE}/events/${event.id}/`, {
                headers: { Authorization: `Token ${user.token}` }
            });
            setEventDetails(eventRes.data);
        } catch (err) {
            const message = err.response?.data?.error || 'Could not start availability collection';
            Alert.alert('Error', message);
        }
    };

    // Check availability and create poll if needed (for organizers)
    const checkAndCreatePoll = async () => {
        try {
            const response = await axios.post(`${API_BASE}/events/${event.id}/check-and-create-poll/`, {}, {
                headers: { Authorization: `Token ${user.token}` }
            });
            
            const data = response.data;
            
            if (data.status === 'polling') {
                Alert.alert('Poll Created', `Multiple suitable time slots found. A poll has been created with ${data.options_count} options.`);
            } else if (data.status === 'confirmed') {
                Alert.alert('Event Confirmed', 'A single suitable time slot was found and the event has been automatically confirmed.');
            } else if (data.missing_participants) {
                const missingList = data.missing_participants.join(', ');
                Alert.alert('Waiting for Participants', `Still waiting for availability from: ${missingList}\n\nSubmitted: ${data.submitted}/${data.total_participants}`);
            } else if (data.status === 'no_slots_found') {
                Alert.alert('No Suitable Slots', 'No time slots were found that work for all participants. You may need to adjust the requirements or manually schedule the event.');
            }
            
            // Refresh event details
            const eventRes = await axios.get(`${API_BASE}/events/${event.id}/`, {
                headers: { Authorization: `Token ${user.token}` }
            });
            setEventDetails(eventRes.data);
        } catch (err) {
            const message = err.response?.data?.error || 'Could not check availability';
            Alert.alert('Error', message);
        }
    };

    // Handle loading state
    if (loading) {
        return (
            <View style={styles.container}>
                <ActivityIndicator size="large" color={colors.primary} />
            </View>
        );
    }

    // Handle error state
    if (error) {
        return (
            <View style={styles.container}>
                <Text style={styles.title}>{error}</Text>
            </View>
        );
    }

    return (
        <ScrollView contentContainerStyle={styles.container}>
            {/* Exit/Back button */}
            <TouchableOpacity 
                onPress={() => navigation.goBack()} 
                style={styles.exitButton}
            >
                <Ionicons name='arrow-back-outline' size={24} color={colors.primary} />
            </TouchableOpacity>

            <View style={{ flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' }}>
                {/* Event title */}
                <Text style={styles.title}>{eventDetails?.title || event.title}</Text>
                
                <View style={{ flexDirection: 'row', alignItems: 'center' }}>
                    {isOrganizer && (
                        <>
                            {/* Edit event */}
                            <TouchableOpacity onPress={editEvent} style={{ marginRight: 12 }}>
                                <Ionicons name='create-outline' size={24} color={colors.containerText} />
                            </TouchableOpacity>
                            {/* Delete event */}
                            <TouchableOpacity onPress={deleteEvent} style={{ marginRight: 12 }}>
                                <Ionicons name='trash-outline' size={24} color={colors.containerText} />
                            </TouchableOpacity>
                        </>
                    )}
                    
                    {!isOrganizer && !isParticipant && (
                        /* Join event */
                        <TouchableOpacity onPress={joinEvent}>
                            <Ionicons name='add-circle-outline' size={24} color={colors.containerText} />
                        </TouchableOpacity>
                    )}
                    
                    {!isOrganizer && isParticipant && (
                        /* Leave event */
                        <TouchableOpacity onPress={leaveEvent}>
                            <Ionicons name='log-out-outline' size={24} color={colors.containerText} />
                        </TouchableOpacity>
                    )}
                </View>
            </View>

            {/* Event details */}
            <View style={styles.detailSection}>
                <Text style={styles.sectionHeader}>Event Details</Text>
                
                {eventDetails?.description && (
                    <View style={styles.detailItem}>
                        <Text style={styles.detailLabel}>Description:</Text>
                        <Text style={styles.detailValue}>{eventDetails.description}</Text>
                    </View>
                )}

                <View style={styles.detailItem}>
                    <Text style={styles.detailLabel}>Start Time:</Text>
                    <Text style={styles.detailValue}>{formatDateTime(eventDetails?.start_time)}</Text>
                </View>

                <View style={styles.detailItem}>
                    <Text style={styles.detailLabel}>End Time:</Text>
                    <Text style={styles.detailValue}>{formatDateTime(eventDetails?.end_time)}</Text>
                </View>

                {eventDetails?.location && (
                    <View style={styles.detailItem}>
                        <Text style={styles.detailLabel}>Location:</Text>
                        <Text style={styles.detailValue}>{eventDetails.location}</Text>
                    </View>
                )}

                <View style={styles.detailItem}>
                    <Text style={styles.detailLabel}>Organizer:</Text>
                    <Text style={styles.detailValue}>{eventDetails?.organizer?.name || 'Unknown'}</Text>
                </View>

                <View style={styles.detailItem}>
                    <Text style={styles.detailLabel}>Group:</Text>
                    <Text style={styles.detailValue}>{eventDetails?.group?.name || 'Unknown'}</Text>
                </View>
            </View>

            {/* Participants */}
            <Text style={styles.sectionHeader}>Participants ({participants.length})</Text>

            {participants.length > 0 ? (
                participants.map((participant, idx) => (
                    <View 
                        key={participant?.user?.id || idx} 
                        style={styles.participantContainer}
                    >
                        <Text style={styles.participant}>
                            {participant?.user?.name || 'Unknown'}
                        </Text>
                        <Text style={styles.participantStatus}>
                            Status: {participant.is_confirmed ? 'Confirmed' : 'Pending'}
                        </Text>
                    </View>
                ))
            ) : (
                <Text style={styles.participant}>No participants yet.</Text>
            )}

            {/* Workflow Actions */}
            <View style={styles.workflowSection}>
                <Text style={styles.sectionHeader}>Event Status: {eventDetails?.status || 'Draft'}</Text>
                
                {/* For Event Creator */}
                {isOrganizer && (
                    <View style={styles.organizerActions}>
                        {eventDetails?.status === 'draft' && (
                            <TouchableOpacity 
                                style={[styles.actionButton, { backgroundColor: colors.primary }]}
                                onPress={startAvailabilityCollection}
                            >
                                <Text style={styles.actionButtonText}>Start Availability Collection</Text>
                            </TouchableOpacity>
                        )}

                        {eventDetails?.status === 'collecting_availability' && (
                            <TouchableOpacity 
                                style={[styles.actionButton, { backgroundColor: colors.containerText }]}
                                onPress={checkAndCreatePoll}
                            >
                                <Text style={styles.actionButtonText}>Check Availability & Create Poll</Text>
                            </TouchableOpacity>
                        )}

                        {eventDetails?.status === 'polling' && eventDetails?.poll && (
                            <TouchableOpacity 
                                style={[styles.actionButton, { backgroundColor: colors.primary }]}
                                onPress={() => navigation.navigate('PollVoting', { 
                                    event: eventDetails, 
                                    poll: eventDetails.poll 
                                })}
                            >
                                <Text style={styles.actionButtonText}>Manage Poll</Text>
                            </TouchableOpacity>
                        )}
                    </View>
                )}

                {/* For Participants */}
                {!isOrganizer && isParticipant && (
                    <View style={styles.participantActions}>
                        {eventDetails?.status === 'collecting_availability' && (
                            <TouchableOpacity 
                                style={[styles.actionButton, { backgroundColor: colors.primary }]}
                                onPress={() => navigation.navigate('AvailabilitySelection', { event: eventDetails })}
                            >
                                <Text style={styles.actionButtonText}>Submit Your Availability</Text>
                            </TouchableOpacity>
                        )}

                        {eventDetails?.status === 'polling' && eventDetails?.poll && (
                            <TouchableOpacity 
                                style={[styles.actionButton, { backgroundColor: colors.primary }]}
                                onPress={() => navigation.navigate('PollVoting', { 
                                    event: eventDetails, 
                                    poll: eventDetails.poll 
                                })}
                            >
                                <Text style={styles.actionButtonText}>Vote for Time Slot</Text>
                            </TouchableOpacity>
                        )}

                        {eventDetails?.status === 'confirmed' && (
                            <View style={[styles.statusCard, { backgroundColor: colors.greyBlue }]}>
                                <Text style={styles.statusText}>
                                    ✅ Event time has been confirmed!
                                </Text>
                                {eventDetails?.confirmed_timeslot && (
                                    <Text style={styles.confirmedTime}>
                                        {formatDateTime(eventDetails.confirmed_timeslot.start_datetime)}
                                    </Text>
                                )}
                            </View>
                        )}
                    </View>
                )}
            </View>
        </ScrollView>
    );
};

export default EventDetail_page;

const styles = StyleSheet.create({
    container: {
        flexGrow: 1,
        padding: 24,
        paddingTop: 80,
        backgroundColor: colors.brownBackground,
    },
    exitButton: {
        flexDirection: 'row',
        alignItems: 'center',
        marginBottom: 16,
        paddingVertical: 8,
    },
    title: {
        fontSize: 24,
        fontFamily: fonts.SemiBold,
        color: colors.primary,
        marginBottom: 8,
        flex: 1,
    },
    detailSection: {
        marginVertical: 16,
    },
    detailItem: {
        marginBottom: 12,
    },
    detailLabel: {
        fontSize: 14,
        fontFamily: fonts.Medium,
        color: colors.primary,
        marginBottom: 4,
    },
    detailValue: {
        fontSize: 16,
        fontFamily: fonts.Regular,
        color: colors.containerText,
        backgroundColor: colors.greyBlue,
        padding: 12,
        borderRadius: 8,
    },
    sectionHeader: {
        fontSize: 18,
        fontFamily: fonts.SemiBold,
        marginTop: 16,
        marginBottom: 12,
        color: colors.primary,
    },
    participantContainer: {
        backgroundColor: colors.greyBlue,
        padding: 16,
        borderRadius: 8,
        marginBottom: 8,
    },
    participant: {
        fontSize: 15,
        fontFamily: fonts.SemiBold,
        color: colors.primary,
        marginBottom: 4,
    },
    participantStatus: {
        fontSize: 13,
        fontFamily: fonts.Regular,
        color: colors.containerText,
    },
    workflowSection: {
        marginTop: 20,
    },
    organizerActions: {
        marginTop: 12,
    },
    participantActions: {
        marginTop: 12,
    },
    actionButton: {
        padding: 16,
        borderRadius: 8,
        alignItems: 'center',
        marginBottom: 12,
    },
    actionButtonText: {
        fontSize: 16,
        fontFamily: fonts.Medium,
        color: colors.white,
    },
    statusCard: {
        padding: 16,
        borderRadius: 8,
        alignItems: 'center',
        marginBottom: 12,
    },
    statusText: {
        fontSize: 16,
        fontFamily: fonts.Medium,
        color: colors.primary,
        textAlign: 'center',
    },
    confirmedTime: {
        fontSize: 14,
        fontFamily: fonts.Regular,
        color: colors.containerText,
        marginTop: 8,
        textAlign: 'center',
    },
});
