import { ActivityIndicator, StyleSheet, Text, TouchableOpacity, View } from 'react-native';
import React, { useEffect, useState } from 'react';
import { colors } from '../utils/colors';
import { API_BASE } from '../utils/config';
import axios from 'axios';
import AntDesign from 'react-native-vector-icons/AntDesign';
import { useUser } from '../context/UserContext';

const getColor = (ratio) => {
    if (ratio >= 0.75) return '#0f62fe';
    if (ratio >= 0.5) return '#5aa9f9';
    if (ratio >= 0.25) return '#a5cffa';
    if (ratio > 0) return '#ddeeff';
   return '#f0f0f0';
};

const HeatmapMonth = ({ isGoogleConnected, onDateSelect, selectedRange }) => {
    const { user } = useUser();
    const [monthOffset, setMonthOffset] = useState(0); // 0  = current month
    const [data, setData] = useState([]);
    const [loading, setLoading] = useState(true);

    const targetDate = new Date();
    targetDate.setMonth(targetDate.getMonth() + monthOffset);
    const year = targetDate.getFullYear();
    const month = targetDate.getMonth();

    useEffect(() => {
        if (!isGoogleConnected) {
            setLoading(false);
            return;
        }
        if (!user?.token) {
            setLoading(false);
            return;
        }
        axios.get(`${API_BASE}/month/`, {
            params: {
                year,
                month: month + 1 // API expects 1-based month
            },
            headers: { Authorization: `Token ${user.token}` }
        })
            .then(res => {
                console.log('API data:', res.data);
                setData(res.data)
            })
            .catch((err) => {
                console.error('HeatmapMonth API error:', err);
                setData([])
            })
            .finally(() => setLoading(false));
    }, [isGoogleConnected, year, month, user]);

    const grouped = {};
    data.forEach(({ date, availableHours, maxHours }) => {
        grouped[date] = maxHours > 0 ? availableHours / maxHours : 0;
    });
    console.log('Grouped ratios:', grouped);

    const firstDay = new Date(year, month, 1);
    const startDay = firstDay.getDay();
    const daysInMonth = new Date(year, month + 1, 0).getDate();

    const grid = [];
    for (let i = 0; i < startDay; i++) grid.push(null);
    for (let day = 1; day <= daysInMonth; day++) {
        const dateStr = `${year}-${(month + 1).toString().padStart(2, '0')}-${day.toString().padStart(2, '0')}`;
        grid.push({ day, ratio: grouped[dateStr] ?? 0});
    }

    const handlePrev = () => setMonthOffset(offset => offset - 1);
    const handleNext = () => setMonthOffset(offset => offset + 1);

    // Helper to check if a date is in the selected range
    const isInRange = (dateStr) => {
        if (!selectedRange?.start || !selectedRange?.end) return false;
        return dateStr >= selectedRange.start && dateStr <= selectedRange.end;
    };
    // Helper to check if a date is the start or end
    const isEdge = (dateStr) => {
        return dateStr === selectedRange?.start || dateStr === selectedRange?.end;
    };

    if (loading) return <ActivityIndicator style = {{ marginTop: 20 }} color = {colors.primary}/>;

  return (
    <View style = {styles.wrapper}>
      <View style = {styles.header}>
        <TouchableOpacity onPress = {handlePrev}>
            <AntDesign name = "left" size = {18} color = {colors.primary}/>
        </TouchableOpacity>
        <Text style = {styles.monthTitle}>
            {targetDate.toLocaleString('default', {month: 'long'})} {year}
        </Text>
        <TouchableOpacity onPress={handleNext}>
            <AntDesign name = "right" size = {18} color = {colors.primary}/>
        </TouchableOpacity>
      </View>

      <View style = {styles.weekHeader}>
        {['S', 'M', 'T', 'W', 'T', 'F', 'S'].map((d, i) => (
            <Text key = {i} style = {styles.weekday}>{d}</Text>
        ))}
      </View>

      <View style = {styles.grid}>
        {grid.map((cell, i) => {
            if (!cell) return <View key={i} style={styles.cell} />;
            const dateStr = `${year}-${(month + 1).toString().padStart(2, '0')}-${cell.day.toString().padStart(2, '0')}`;
            const isSelected = isInRange(dateStr);
            const isEdgeDay = isEdge(dateStr);
            return (
                <TouchableOpacity
                  key={i}
                  style={[
                    styles.cell,
                    { backgroundColor: isSelected ? (isEdgeDay ? '#7ecbff' : '#cbeafe') : getColor(cell.ratio),
                      borderWidth: isEdgeDay ? 2 : 0,
                      borderColor: isEdgeDay ? '#4fc3f7' : 'transparent',
                    }
                  ]}
                  onPress={() => onDateSelect && onDateSelect(dateStr)}
                >
                  <Text style={styles.cellText}>{cell.day}</Text>
                </TouchableOpacity>
            );
        })}
      </View>

      {!isGoogleConnected && (
        <Text style = {styles.noteText}>Google Calendar not connected. No availability data shown</Text>
      )}
    </View>
  );
};

export default HeatmapMonth

const styles = StyleSheet.create({
    wrapper: {
        alignItems: 'center',
    },
    header: {
        flexDirection: 'row',
        alignItems: 'center',
        justifyContent: 'space-between',
        width: 240,
        marginBottom: 8,
    },
    monthTitle: {
        fontSize: 18,
        fontFamily: 'Poppins-Semibold',
        color: colors.primary,
    },
    weekHeader: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        width: '100%',
        paddingHorizontal: 39,
        paddingTop: 10,
        marginBottom: 4,
    },
    weekday: {
        width: 30,
        textAlign: 'center',
        fontSize: 12,
        color: colors.containerText,
    },
    grid: {
        flexDirection: 'row',
        flexWrap: 'wrap',
        width: 300,
    },
    cell: {
        width: 40,
        height: 40,
        margin: 1,
        justifyContent: 'center',
        alignItems: 'center',
        borderRadius: 4,
    },
    cellText: {
        fontSize: 10,
        color: '#000',
    },
    noteText: {
        fontSize: 12,
        color: colors.containerText,
        marginTop: 12,
        fontFamily: 'Poppins-Regular',
        textAlign: 'center',
    },
});