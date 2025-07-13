import { StyleSheet, Text, View, TouchableOpacity, TextInput, Modal, ScrollView, Alert } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import React, { useState, useEffect } from 'react';
import DropDownPicker from 'react-native-dropdown-picker';
import RNCalendarEvents from 'react-native-calendar-events';
import Ionicons from 'react-native-vector-icons/Ionicons';
import { colors } from '../utils/colors';
import { fonts } from '../utils/fonts';
import { useNavigation } from '@react-navigation/native';
import HeatmapMonth from '../components/HeatmapMonth';
import { API_BASE } from '../utils/config';
import axios from 'axios';
import { Picker } from '@react-native-picker/picker';

const CreateEvent_page = ({ visible, onClose, onCreate }) => {
    const [title, setTitle] = useState('');
    const [description, setDescription] = useState('');

    const [selectedRange, setSelectedRange] = useState({ start: null, end: null });

    const [selectedGroup, setSelectedGroup] = useState(null);
    const [groupOptions, setGroupOptions] = useState([]);
    const [groupsLoading, setGroupsLoading] = useState(true);
    const [groupPickerOpen, setGroupPickerOpen] = useState(false);

    const [mode, setMode] = useState(null);
    const [modePickerOpen, setModePickerOpen] = useState(false);
    const [modeOptions] = useState([
        { label: 'Online', value: 'online' },
        { label: 'In-person', value: 'inperson' },
    ]);

    const [durationHour, setDurationHour] = useState(1);
    const [durationHourPickerOpen, setDurationHourPickerOpen] = useState(false);
    const [durationMinute, setDurationMinute] = useState(0);
    const [durationMinutePickerOpen, setDurationMinutePickerOpen] = useState(false);
    const hourOptions = Array.from({ length: 12 }, (_, i) => ({ label: `${i+1} hr`, value: i+1 }));
    const minuteOptions = [0, 15, 30, 45].map(m => ({ label: `${m} min`, value: m }));

    const navigation = useNavigation();

    useEffect(() => {
        RNCalendarEvents.requestPermissions();
    }, []);

    useEffect(() => {
        // Fetch groups from backend
        const fetchGroups = async () => {
            try {
                const res = await axios.get(`${API_BASE}/groups/`);
                if (Array.isArray(res.data) && res.data.length > 0) {
                    setGroupOptions(res.data.map(group => ({ label: group.name, value: group.id })));
                } else {
                    setGroupOptions([]);
                }
            } catch (error) {
                setGroupOptions([]);
            } finally {
                setGroupsLoading(false);
            }
        };
        fetchGroups();
    }, []);

    // Handler for selecting a date from the heatmap
    const handleDateSelect = (date) => {
        if (!selectedRange.start || (selectedRange.start && selectedRange.end)) {
            setSelectedRange({ start: date, end: null });
        } else if (selectedRange.start && !selectedRange.end) {
            if (date < selectedRange.start) {
                setSelectedRange({ start: date, end: selectedRange.start });
            } else {
                setSelectedRange({ start: selectedRange.start, end: date });
            }
        }
    };

    const handleCreate = async () => {
        if (!title.trim()) {
            Alert.alert("Title is required");
            return;
        }
        if (!selectedRange.start || !selectedRange.end) {
            Alert.alert("Please select a date range for the event");
            return;
        }
        const totalDuration = durationHour * 60 + durationMinute;
        const newEvent = {
            id: Date.now().toString(),
            title,
            description,
            mode,
            duration: totalDuration,
            host: true, // Optional
            startDate: selectedRange.start,
            endDate: selectedRange.end,
        };
        try {
            await RNCalendarEvents.saveEvent(title, {
                startDate: selectedRange.start.toISOString(),
                endDate: selectedRange.end.toISOString(),
                notes: description,
            });
            Alert.alert('Event added to your device calendar!');
        } catch (e) {
            Alert.alert('Failed to add event to calendar', e.message);
        }
        navigation.navigate('Main', { newEvent });
        setTitle('');
        setDescription('');
        setMode('');
        setDuration('');
        setSelectedRange({ start: null, end: null });
    };

    // Add this function to reset all fields and close the modal/page
    const handleCancel = () => {
        setTitle('');
        setDescription('');
        setMode('');
        setDuration('');
        setSelectedRange({ start: null, end: null });
        setSelectedGroup('');
        navigation.navigate('Main');
    };


  return (
    <View style = {styles.container}>
        <SafeAreaView style = {styles.container}>
            <View style = {styles.headerContainer}>
                <TouchableOpacity style = {styles.cancelContainer} onPress = {handleCancel}>
                    <Text style = {styles.cancelText}>Cancel</Text>
                </TouchableOpacity>

                <Text style = {styles.headerText}>Create New Event</Text>

                <TouchableOpacity onPress = {handleCreate}>
                    <Text style = {styles.newText}>New</Text>
                </TouchableOpacity>
            </View>

            <ScrollView contentContainerStyle = {{ paddingBottom: 30 }}>
                <TextInput
                style = {styles.input}
                placeholder = 'Title'
                value = {title}
                onChangeText = {setTitle}
                />

                <TextInput
                    style = {styles.input}
                    placeholder = 'Description (Optional)'
                    value = {description}
                    onChangeText = {setDescription}
                />

                <View style = {styles.detailsContainer}>

                    <View style={{ zIndex: 2, marginBottom: 20 }}>
                      <Text style={styles.dropdownLabel}>In-person / Online</Text>
                      <DropDownPicker
                        open={modePickerOpen}
                        value={mode}
                        items={modeOptions}
                        setOpen={setModePickerOpen}
                        setValue={setMode}
                        setItems={() => {}}
                        placeholder="Select"
                        style={{ backgroundColor: colors.dropdownContainer, borderWidth: 0 }}
                        textStyle={{ color: colors.containerText }}
                        dropDownContainerStyle={{ backgroundColor: colors.container }}
                        listMode="SCROLLVIEW"
                      />
                    </View>

                    <Text style={styles.dropdownLabel}>Duration</Text>
                    <View style={{ flexDirection: 'row', alignItems: 'center', justifyContent: 'center', marginBottom: 20, backgroundColor: colors.dropdownContainer, borderRadius: 10, paddingHorizontal: 5, paddingVertical: 2, height: 60, width: '100%' }}>
                      <View style={{ width: '100%' }}>

                        <View style={{ flexDirection: 'row', alignItems: 'center', justifyContent: 'center', width: '100%' }}>
                        <Picker
                          selectedValue={durationHour}
                          onValueChange={setDurationHour}
                          style={{ color: colors.containerText, fontSize: 16, width: 100, height: 40 }}
                          itemStyle={{ fontSize: 16, color: colors.containerText, height: 40 }}
                          mode="dropdown"
                        >
                          {Array.from({ length: 12 }, (_, i) => (
                            <Picker.Item key={i+1} label={`${i+1}`} value={i+1} style={{ fontSize: 16, height: 40 }} />
                          ))}
                        </Picker>
                        <Text style={{ color: colors.containerText, fontSize: 18, marginHorizontal: 6 }}>:</Text>
                        <Picker
                          selectedValue={durationMinute}
                          onValueChange={setDurationMinute}
                          style={{ color: colors.containerText, fontSize: 16, width: 100, height: 40 }}
                          itemStyle={{ fontSize: 16, color: colors.containerText, height: 40 }}
                          mode="dropdown"
                        >
                          {[0, 15, 30, 45].map(m => (
                            <Picker.Item key={m} label={m < 10 ? `0${m}` : `${m}`} value={m} style={{ fontSize: 16, height: 40 }} />
                          ))}
                        </Picker>
                      </View>
                    </View>
                  </View>

                </View>

                <Text style = {styles.sectionTitle}>Select Date Range</Text>
                <Text style={{fontSize:12, color:'gray', marginBottom:10}}>
                  {selectedRange.start && selectedRange.end ? `Selected: ${selectedRange.start} to ${selectedRange.end}` : 'Tap to select start and end dates'}
                </Text>
                <View style={{marginBottom: 20}}>
                  <HeatmapMonth isGoogleConnected={true} onDateSelect={handleDateSelect} selectedRange={selectedRange} />
                </View>


                <Text style = {styles.sectionTitle}>Add Group</Text>
                <View style={styles.input}>
                  {groupsLoading ? (
                    <Text style={{ color: 'gray', fontSize: 14 }}>Loading groups...</Text>
                  ) : groupOptions.length === 0 ? (
                    <Text style={{ color: 'gray', fontSize: 14 }}>You are in no groups</Text>
                  ) : (
                    <DropDownPicker
                      open={groupPickerOpen}
                      value={selectedGroup}
                      items={groupOptions}
                      setOpen={setGroupPickerOpen}
                      setValue={setSelectedGroup}
                      setItems={setGroupOptions}
                      placeholder="Select Group"
                      style={{ backgroundColor: colors.dropdownContainer }}
                      textStyle={{ color: colors.containerText }}
                      dropDownContainerStyle={{ backgroundColor: colors.container }}
                      listMode="SCROLLVIEW"
                    />
                  )}
                </View>

            </ScrollView>
        </SafeAreaView>
    </View>
  )
}

export default CreateEvent_page

const styles = StyleSheet.create({
    container: {
        flex: 1,
        padding: 15,
        paddingTop: 20,
        backgroundColor: colors.white,
    },

    headerContainer: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: 10,
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
    newText: {
        color: colors.primary,
        fontFamily: fonts.SemiBold,
    },

    input: {
        backgroundColor: colors.container,
        borderRadius: 10,
        padding: 15,
        marginBottom: 10,
    },

    detailsContainer: {
        marginTop: 30,
    },

    dropdownSection: {
        flexDirection: 'row',
        alignItems: 'center',
        overflow: 'visible',
        backgroundColor: colors.container,
        borderRadius: 10,
        padding: 15,
        marginBottom: 15,
    },    
    dropdownLabel: {
        fontFamily: fonts.SemiBold,
        fontSize: 14,
        color: colors.primary,
        marginBottom: 5,
        flex: 2,
    },

    pickerWrapper: {
        marginBottom: 10,
        backgroundColor: colors.dropdownContainer,
        flex: 1,
        borderRadius: 5,
        height: 45,
        justifyContent: 'center',
    },

    picker: {
        color: colors.containerText,
        fontFamily: fonts.Regular,
        height: 40,
        fontSize: 10,
    },

    sectionTitle: {
        fontFamily: fonts.SemiBold,
        marginBottom: 10,
        fontSize: 16,
        color: colors.primary,
    },

    calendarBox: {
        height: 200,
        backgroundColor: colors.white,
        borderRadius: 10,
        justifyContent: 'center',
        alignItems: 'center',
        marginBottom: 20,
    },
    username: {
        color: colors.containerText,
        fontFamily: fonts.Regular,
    },
})