import { ActivityIndicator, StyleSheet, Text, TouchableOpacity, View } from 'react-native';
import React, { useEffect, useState } from 'react';
import { colors } from '../utils/colors';
import { BASE_URL } from '../utils/config';
import axios from 'axios';
import AntDesign from 'react-native-vector-icons/AntDesign';

const getColor = (ratio) => {
    if (ratio >= 0.75) return '#0f62fe';
    if (ratio >= 0.5) return '#5aa9f9';
    if (ratio >= 0.25) return '#a5cffa';
    if (ratio > 0) return '#ddeeff';
   return '#f0f0f0';
};

const HeatmapMonth = ({ isGoogleConnected }) => {
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

        axios.get(`${BASE_URL}/api/availcalendar/month`, {
            params: {
                year,
                month: month + 1 // API expects 1-based month
            }
        })
            .then(res => setData(res.data))
            .catch(() => setData([]))
            .finally(() => setLoading(false));
    }, [isGoogleConnected, year, month]);

    const grouped = {};
    data.forEach(({ date, availableHours, maxHours }) => {
        grouped[date] = maxHours > 0 ? availableHours / maxHours : 0;
    });

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
        {grid.map((cell, i) => (
            <View key = {i} style = {[styles.cell, { backgroundColor: getColor(cell?.ratio) }]}>
                {cell && <Text style = {styles.cellText}>{cell.day}</Text>}
            </View>
        ))}
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