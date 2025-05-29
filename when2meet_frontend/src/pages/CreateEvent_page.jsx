import { StyleSheet, Text, View, TouchableOpacity, TextInput, Modal, ScrollView, Alert } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import React, { useState } from 'react';
import RNPickerSelect from 'react-native-picker-select';
import { Picker } from '@react-native-picker/picker';
import Ionicons from 'react-native-vector-icons/Ionicons';
import { colors } from '../utils/colors';
import { fonts } from '../utils/fonts';

const CreateEvent_page = ({ visible, onClose, onCreate }) => {
    const [title, setTitle] = useState('');
    const [description, setDescription] = useState('');

    const [mode, setMode] = useState('');
    const [duration, setDuration] = useState('');

    const pickerSelectStyles = {
        inputIOS: {
            fontSize: 14,
            backgroundColor: colors.dropdownContainer,
            color: colors.containerText,
            paddingVertical: 8,
            paddingHorizontal: 12,
            borderRadius: 6,
            width: 100,
        },
        inputAndroid: {
            fontSize: 14,
            backgroundColor: colors.dropdownContainer,
            color: colors.containerText,
            paddingVertical: 8,
            paddingHorizontal: 12,
            borderRadius: 6,
        },
        iconContainer: {
            top: 10,
            right: 5,
        },
        };


    const handleCreate = () => {
        if (!title.trim()) {
            Alert.alert("Title is required");
            return;
        }

        const newEvent = {
            id: Date.now().toString(),
            title,
            description,
            mode,
            duration,
            host: true, // Optional
        };

        onCreate(newEvent);  // send back to parent
        onClose(); // close modal after creating
        setTitle('');
        setDescription('');
        setMode('');
        setDuration('');
    };


  return (
    <Modal visible = {visible} animationType = 'slide'>
        <SafeAreaView style = {styles.container}>
            <View style = {styles.headerContainer}>
                <TouchableOpacity style = {styles.cancelContainer} onPress = {onClose}>
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
                    <View style = {styles.dropdownSection}>
                        <Text style = {styles.dropdownLabel}>In-person / Online</Text>
                        <RNPickerSelect
                            onValueChange = {(value) => setMode(value)}
                            items = {[
                                { label: 'Online', value: 'online', key: 'online' },
                                { label: 'In-person', value: 'inperson', key: 'inperson' },
                            ]}
                            value = {mode}
                            placeholder = {{label: "Select", value: null}}
                            style = {pickerSelectStyles}
                            useNativeAndroidPickerStyle = {false}
                            Icon = {() => <Ionicons name = "chevron-down" size = {18} color = {colors.containerText}/>}
                        />
                    </View>

                    <View style = {styles.dropdownSection}>
                        <Text style = {styles.dropdownLabel}>Duration</Text>
                        <RNPickerSelect
                            onValueChange = {(value) => setDuration(value)}
                            items = {[
                                { label: '30 mins', value: '30', key: '30' },
                                { label: '1 hr', value: '60', key: '60' },
                                { label: '1 hr 30 mins', value: '90', key: '90'},
                                { label: '2 hr', value: '120', key: '120'},
                            ]}
                            value = {duration}
                            placeholder = {{label: "Select", value: null}}
                            style = {pickerSelectStyles}
                            useNativeAndroidPickerStyle = {false}
                            Icon = {() => <Ionicons name = "chevron-down" size = {18} color = {colors.containerText}/>}
                        />
                    </View>
                </View>

                <Text style = {styles.sectionTitle}>Select Dates & Time</Text>
                {/* Dummy calendar representation */}
                <View style = {styles.calendarBox}><Text>[ Calendar grid placeholder ]</Text></View>

            </ScrollView>
        </SafeAreaView>
    </Modal>
  )
}

export default CreateEvent_page

const styles = StyleSheet.create({
    container: {
        flex: 1,
        padding: 30,
        paddingTop: 50,
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
    newText: {
        color: colors.primary,
        fontFamily: fonts.SemiBold,
    },

    input: {
        backgroundColor: colors.container,
        borderRadius: 10,
        padding: 15,
        marginBottom: 15,
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
        marginBottom: 20,
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