import React, { useState, useEffect, useContext } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  FlatList,
  Alert,
  ActivityIndicator,
} from 'react-native';
import { UserContext } from '../context/UserContext';
import { colors } from '../utils/colors';
import { fonts } from '../utils/fonts';

const PollVoting_page = ({ route, navigation }) => {
  const { event, poll } = route.params;
  const { user } = useContext(UserContext);
  const [pollOptions, setPollOptions] = useState([]);
  const [selectedOption, setSelectedOption] = useState(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [hasVoted, setHasVoted] = useState(false);

  useEffect(() => {
    loadPollOptions();
  }, []);

  const loadPollOptions = async () => {
    try {
      const response = await fetch(
        `http://localhost:8000/polls/${poll.id}/options/`,
        {
          headers: {
            'Authorization': `Bearer ${user.token}`,
            'Content-Type': 'application/json',
          }
        }
      );

      if (response.ok) {
        const data = await response.json();
        setPollOptions(data);
        
        // Check if user has already voted
        const userVote = data.find(option => 
          option.votes && option.votes.some(vote => vote.voter_id === user.profile_id)
        );
        
        if (userVote) {
          setHasVoted(true);
          setSelectedOption(userVote.id);
        }
      }
    } catch (error) {
      console.error('Error loading poll options:', error);
      Alert.alert('Error', 'Failed to load poll options');
    } finally {
      setLoading(false);
    }
  };

  const submitVote = async () => {
    if (!selectedOption) {
      Alert.alert('Error', 'Please select an option to vote');
      return;
    }

    setSubmitting(true);
    try {
      const response = await fetch(
        'http://localhost:8000/poll-votes/',
        {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${user.token}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            poll_option: selectedOption
          })
        }
      );

      if (response.ok) {
        Alert.alert(
          'Success',
          'Your vote has been submitted!',
          [{ text: 'OK', onPress: () => navigation.goBack() }]
        );
      } else {
        const errorData = await response.json();
        Alert.alert('Error', errorData.error || 'Failed to submit vote');
      }
    } catch (error) {
      Alert.alert('Error', 'Network error. Please try again.');
    } finally {
      setSubmitting(false);
    }
  };

  const formatDateTime = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], {
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const renderPollOption = ({ item }) => {
    const isSelected = selectedOption === item.id;
    const voteCount = item.votes ? item.votes.length : 0;
    
    return (
      <TouchableOpacity
        style={[
          styles.optionCard,
          {
            borderColor: isSelected ? colors.primary : colors.border,
            backgroundColor: isSelected ? colors.primaryLight : colors.surface,
          }
        ]}
        onPress={() => !hasVoted && setSelectedOption(item.id)}
        disabled={hasVoted}
      >
        <View style={styles.optionHeader}>
          <View style={styles.optionInfo}>
            <Text style={[
              styles.optionTime,
              { 
                color: isSelected ? colors.primary : colors.text,
                fontFamily: fonts.medium 
              }
            ]}>
              {formatDateTime(item.timeslot.start_datetime)}
            </Text>
            <Text style={[
              styles.optionDuration,
              { color: colors.textSecondary }
            ]}>
              to {formatDateTime(item.timeslot.end_datetime)}
            </Text>
          </View>
          
          <View style={styles.voteInfo}>
            <Text style={[
              styles.voteCount,
              { 
                color: isSelected ? colors.primary : colors.text,
                fontFamily: fonts.medium 
              }
            ]}>
              {voteCount} vote{voteCount !== 1 ? 's' : ''}
            </Text>
          </View>
        </View>

        {item.timeslot.description && (
          <Text style={[styles.optionDescription, { color: colors.textSecondary }]}>
            {item.timeslot.description}
          </Text>
        )}

        {isSelected && (
          <View style={[styles.selectedIndicator, { backgroundColor: colors.primary }]}>
            <Text style={[styles.selectedText, { color: colors.white }]}>
              ✓ Selected
            </Text>
          </View>
        )}
      </TouchableOpacity>
    );
  };

  if (loading) {
    return (
      <View style={[styles.loadingContainer, { backgroundColor: colors.background }]}>
        <ActivityIndicator size="large" color={colors.primary} />
        <Text style={[styles.loadingText, { color: colors.text }]}>
          Loading poll options...
        </Text>
      </View>
    );
  }

  return (
    <View style={[styles.container, { backgroundColor: colors.background }]}>
      <View style={styles.header}>
        <Text style={[styles.title, { color: colors.text, fontFamily: fonts.bold }]}>
          Vote for Your Preferred Time
        </Text>
        <Text style={[styles.eventTitle, { color: colors.primary, fontFamily: fonts.medium }]}>
          {event.title}
        </Text>
        
        {hasVoted && (
          <View style={[styles.votedBanner, { backgroundColor: colors.success }]}>
            <Text style={[styles.votedText, { color: colors.white }]}>
              ✓ You have already voted
            </Text>
          </View>
        )}
      </View>

      <FlatList
        data={pollOptions}
        renderItem={renderPollOption}
        keyExtractor={(item) => item.id.toString()}
        style={styles.optionsList}
        showsVerticalScrollIndicator={false}
      />

      {!hasVoted && (
        <TouchableOpacity
          style={[
            styles.submitButton,
            {
              backgroundColor: selectedOption ? colors.primary : colors.disabled,
            }
          ]}
          onPress={submitVote}
          disabled={submitting || !selectedOption}
        >
          {submitting ? (
            <ActivityIndicator color={colors.white} />
          ) : (
            <Text style={[styles.submitButtonText, { color: colors.white, fontFamily: fonts.bold }]}>
              Submit Vote
            </Text>
          )}
        </TouchableOpacity>
      )}

      <TouchableOpacity
        style={[styles.viewResultsButton, { borderColor: colors.primary }]}
        onPress={() => navigation.navigate('PollResults', { event, poll })}
      >
        <Text style={[styles.viewResultsText, { color: colors.primary, fontFamily: fonts.medium }]}>
          View Current Results
        </Text>
      </TouchableOpacity>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 20,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  loadingText: {
    marginTop: 10,
    fontSize: 16,
  },
  header: {
    marginBottom: 20,
  },
  title: {
    fontSize: 24,
    marginBottom: 8,
  },
  eventTitle: {
    fontSize: 18,
    marginBottom: 10,
  },
  votedBanner: {
    padding: 12,
    borderRadius: 8,
    alignItems: 'center',
    marginTop: 10,
  },
  votedText: {
    fontSize: 16,
    fontWeight: '500',
  },
  optionsList: {
    flex: 1,
    marginBottom: 20,
  },
  optionCard: {
    padding: 15,
    borderRadius: 12,
    borderWidth: 2,
    marginBottom: 12,
    position: 'relative',
  },
  optionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
  },
  optionInfo: {
    flex: 1,
  },
  optionTime: {
    fontSize: 16,
    marginBottom: 4,
  },
  optionDuration: {
    fontSize: 14,
  },
  voteInfo: {
    alignItems: 'flex-end',
  },
  voteCount: {
    fontSize: 14,
  },
  optionDescription: {
    fontSize: 14,
    marginTop: 8,
    fontStyle: 'italic',
  },
  selectedIndicator: {
    position: 'absolute',
    top: 10,
    right: 10,
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 4,
  },
  selectedText: {
    fontSize: 12,
    fontWeight: '500',
  },
  submitButton: {
    padding: 18,
    borderRadius: 8,
    alignItems: 'center',
    marginBottom: 12,
  },
  submitButtonText: {
    fontSize: 18,
  },
  viewResultsButton: {
    padding: 15,
    borderRadius: 8,
    borderWidth: 2,
    alignItems: 'center',
  },
  viewResultsText: {
    fontSize: 16,
  },
});

export default PollVoting_page;
