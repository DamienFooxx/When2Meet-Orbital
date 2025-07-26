import { StyleSheet, Text, View, TouchableOpacity } from 'react-native'
import React, { useEffect, useState } from 'react'
import AntDesign from 'react-native-vector-icons/AntDesign';
import { useNavigation } from '@react-navigation/native';
import { colors } from '../utils/colors';
import { fonts } from '../utils/fonts';
import HeatmapMonth from '../components/HeatmapMonth';
import axios from 'axios';
import { API_BASE } from '../utils/config';
import { useUser } from '../context/UserContext';

const Calendar_page = () => {
    const [view, setView]  = useState("month");
    const [syncing, setSyncing] = useState(false);
    const navigation = useNavigation();
    const { user } = useUser();

    const handleSync = async () => {
        if (!user?.token) {
            alert('You must be logged in to sync.');
            return;
        }
        setSyncing(true);
        try {
            // Sync for the current month
            const now = new Date();
            const year = now.getFullYear();
            const month = now.getMonth() + 1;
            const start = `${year}-${month.toString().padStart(2, '0')}-01`;
            const end = `${year}-${month.toString().padStart(2, '0')}-31`;
            await axios.put(
                `${API_BASE}/sync/google/`,
                { start, end },
                { headers: { Authorization: `Token ${user.token}` } }
            );
            alert('Google Calendar sync started! Refresh in a few seconds.');
        } catch (e) {
            alert('Failed to sync Google Calendar.');
        } finally {
            setSyncing(false);
        }
    }

    return (
        <View style={styles.container}>
            <View style={styles.topBar}>
                <TouchableOpacity onPress={() => navigation.goBack()}>
                    <AntDesign name="left" size={24} color={colors.primary} />
                </TouchableOpacity>
                <Text style={styles.header}>Calendar</Text>
                <TouchableOpacity onPress={handleSync} style={{marginLeft: 'auto', padding: 8, opacity: syncing ? 0.5 : 1}} disabled={syncing}>
                  <Text style={{color: colors.primary, fontFamily: fonts.Medium}}>{syncing ? 'Syncing...' : 'Sync'}</Text>
                </TouchableOpacity>
            </View>
            <View style={styles.toggleBar}>
                <TouchableOpacity
                    style={[styles.toggleButton, view === 'month' && styles.activeToggle]}
                    onPress={() => setView('month')}
                >
                    <Text style={[styles.toggleText, view === 'month' && styles.activeToggleText]}>Month</Text>
                </TouchableOpacity>
                <TouchableOpacity
                    style={[styles.toggleButton, view === 'week' && styles.activeToggle]}
                    onPress={() => setView('week')}
                >
                    <Text style={[styles.toggleText, view === 'week' && styles.activeToggleText]}>Week</Text>
                </TouchableOpacity>
            </View>
            {view === 'month' && <HeatmapMonth isGoogleConnected={true} />} 
            {/* Replace true with actual prop if needed */}
            {view === 'week' && (
                <View style={styles.placeholder}><Text>Week view coming soon!</Text></View>
            )}
        </View>
    );
}

export default Calendar_page

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: colors.white,
        paddingTop: 60,
        paddingHorizontal: 16,
    },
    topBar: {
        flexDirection: 'row',
        alignItems: 'center',
        marginBottom: 20,
        gap: 10,
    },
    header: {
        fontSize: 22,
        fontFamily: fonts.SemiBold,
        color: colors.primary,
        marginLeft: 10,
    },
    toggleBar: {
        flexDirection: 'row',
        justifyContent: 'center',
        marginBottom: 20,
        gap: 10,
    },
    toggleButton: {
        paddingVertical: 8,
        paddingHorizontal: 20,
        borderRadius: 20,
        backgroundColor: colors.lightBlue,
    },
    activeToggle: {
        backgroundColor: colors.primary,
    },
    toggleText: {
        color: colors.primary,
        fontFamily: fonts.Medium,
        fontSize: 16,
    },
    activeToggleText: {
        color: colors.white,
    },
    placeholder: {
        flex: 1,
        alignItems: 'center',
        justifyContent: 'center',
    },
});