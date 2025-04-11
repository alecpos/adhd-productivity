import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, ScrollView, TextInput, TouchableOpacity, Alert } from 'react-native';
import { Card, Button, Icon, Chip, CheckBox, FAB, Overlay } from '@rneui/themed';
import { format } from 'date-fns';

interface Commitment {
  id: string;
  text: string;
  dueDate: string | null;
  priority: 'high' | 'medium' | 'low';
  status: 'pending' | 'completed' | 'missed';
  source: string;
  confidence: number;
  relatedCommitments: string[];
  created: string;
}

// Mock data for demonstration
const mockCommitments: Commitment[] = [
  {
    id: '1',
    text: 'Send the project proposal to Alex by Thursday',
    dueDate: '2023-03-10T17:00:00',
    priority: 'high',
    status: 'pending',
    source: 'Email',
    confidence: 0.92,
    relatedCommitments: ['3'],
    created: '2023-03-05T10:23:00'
  },
  {
    id: '2',
    text: 'Schedule a meeting with the team to discuss Q2 goals',
    dueDate: '2023-03-15T12:00:00',
    priority: 'medium',
    status: 'pending',
    source: 'Chat',
    confidence: 0.85,
    relatedCommitments: [],
    created: '2023-03-06T14:30:00'
  },
  {
    id: '3',
    text: 'Review the project timeline and update milestones',
    dueDate: '2023-03-12T17:00:00',
    priority: 'high',
    status: 'pending',
    source: 'Journal',
    confidence: 0.78,
    relatedCommitments: ['1'],
    created: '2023-03-06T09:15:00'
  },
  {
    id: '4',
    text: 'Call Dr. Johnson to schedule annual checkup',
    dueDate: '2023-03-08T17:00:00',
    priority: 'medium',
    status: 'completed',
    source: 'Journal',
    confidence: 0.89,
    relatedCommitments: [],
    created: '2023-03-04T16:45:00'
  },
  {
    id: '5',
    text: 'Buy groceries for dinner party',
    dueDate: '2023-03-09T15:00:00',
    priority: 'low',
    status: 'pending',
    source: 'Chat',
    confidence: 0.94,
    relatedCommitments: [],
    created: '2023-03-07T11:20:00'
  }
];

export const CommitmentTracker = () => {
  const [commitments, setCommitments] = useState<Commitment[]>(mockCommitments);
  const [filteredCommitments, setFilteredCommitments] = useState<Commitment[]>(mockCommitments);
  const [selectedStatus, setSelectedStatus] = useState<string>('pending');
  const [searchQuery, setSearchQuery] = useState('');
  const [showDialog, setShowDialog] = useState(false);
  const [dialogText, setDialogText] = useState('');
  const [showRelated, setShowRelated] = useState<string | null>(null);

  useEffect(() => {
    // Filter commitments based on selected status and search query
    let filtered = commitments;

    if (selectedStatus !== 'all') {
      filtered = filtered.filter(item => item.status === selectedStatus);
    }

    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(item =>
        item.text.toLowerCase().includes(query) ||
        (item.source && item.source.toLowerCase().includes(query))
      );
    }

    setFilteredCommitments(filtered);
  }, [commitments, selectedStatus, searchQuery]);

  const handleStatusChange = (status: string) => {
    setSelectedStatus(status);
  };

  const handleComplete = (id: string) => {
    setCommitments(prevCommitments =>
      prevCommitments.map(item =>
        item.id === id ? { ...item, status: 'completed' } : item
      )
    );
  };

  const handleDelete = (id: string) => {
    Alert.alert(
      'Delete Commitment',
      'Are you sure you want to delete this commitment?',
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Delete',
          onPress: () => {
            setCommitments(prevCommitments =>
              prevCommitments.filter(item => item.id !== id)
            );
          },
          style: 'destructive'
        }
      ]
    );
  };

  const handleAddCommitment = () => {
    if (!dialogText.trim()) return;

    // Simulate AI analysis of commitment text
    setTimeout(() => {
      const newCommitment: Commitment = {
        id: (commitments.length + 1).toString(),
        text: dialogText,
        dueDate: '2023-03-20T17:00:00', // Example date
        priority: 'medium',
        status: 'pending',
        source: 'Manual Entry',
        confidence: 1.0, // Manual entry has 100% confidence
        relatedCommitments: [],
        created: new Date().toISOString()
      };

      setCommitments(prev => [newCommitment, ...prev]);
      setDialogText('');
      setShowDialog(false);
    }, 500);
  };

  const getRelatedCommitments = (commitmentId: string) => {
    const relatedIds = commitments.find(c => c.id === commitmentId)?.relatedCommitments || [];
    return commitments.filter(c => relatedIds.includes(c.id));
  };

  const formatDate = (dateString: string | null) => {
    if (!dateString) return 'No date';
    try {
      return format(new Date(dateString), 'MMM d, yyyy h:mm a');
    } catch (e) {
      return 'Invalid date';
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high': return '#DA4747';
      case 'medium': return '#DAA147';
      case 'low': return '#47DA9B';
      default: return '#888888';
    }
  };

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>Commitment Tracker</Text>
        <TextInput
          style={styles.searchInput}
          placeholder="Search commitments..."
          value={searchQuery}
          onChangeText={setSearchQuery}
        />
      </View>

      <View style={styles.filterContainer}>
        <ScrollView horizontal showsHorizontalScrollIndicator={false}>
          <Chip
            title="Pending"
            type={selectedStatus === 'pending' ? 'solid' : 'outline'}
            onPress={() => handleStatusChange('pending')}
            containerStyle={styles.chipContainer}
            buttonStyle={selectedStatus === 'pending' ? styles.activeChip : styles.inactiveChip}
          />
          <Chip
            title="Completed"
            type={selectedStatus === 'completed' ? 'solid' : 'outline'}
            onPress={() => handleStatusChange('completed')}
            containerStyle={styles.chipContainer}
            buttonStyle={selectedStatus === 'completed' ? styles.activeChip : styles.inactiveChip}
          />
          <Chip
            title="Missed"
            type={selectedStatus === 'missed' ? 'solid' : 'outline'}
            onPress={() => handleStatusChange('missed')}
            containerStyle={styles.chipContainer}
            buttonStyle={selectedStatus === 'missed' ? styles.activeChip : styles.inactiveChip}
          />
          <Chip
            title="All"
            type={selectedStatus === 'all' ? 'solid' : 'outline'}
            onPress={() => handleStatusChange('all')}
            containerStyle={styles.chipContainer}
            buttonStyle={selectedStatus === 'all' ? styles.activeChip : styles.inactiveChip}
          />
        </ScrollView>
      </View>

      <ScrollView style={styles.scrollContainer}>
        {filteredCommitments.length === 0 ? (
          <View style={styles.emptyState}>
            <Icon name="clipboard-text-outline" type="material-community" size={48} color="#888888" />
            <Text style={styles.emptyText}>No commitments found</Text>
          </View>
        ) : (
          filteredCommitments.map(commitment => (
            <View key={commitment.id}>
              <Card containerStyle={styles.card}>
                <View style={styles.cardHeader}>
                  <View style={styles.titleContainer}>
                    <View style={styles.priorityIndicator}>
                      <View style={[styles.priorityDot, { backgroundColor: getPriorityColor(commitment.priority) }]} />
                      <Text style={styles.priorityText}>{commitment.priority.charAt(0).toUpperCase() + commitment.priority.slice(1)}</Text>
                    </View>
                    <Text style={styles.sourceText}>{commitment.source} • {Math.round(commitment.confidence * 100)}% confidence</Text>
                  </View>
                  {commitment.status !== 'completed' && (
                    <CheckBox
                      checked={commitment.status === 'completed'}
                      onPress={() => handleComplete(commitment.id)}
                      containerStyle={styles.checkbox}
                    />
                  )}
                </View>

                <Text style={styles.commitmentText}>{commitment.text}</Text>

                <View style={styles.dateContainer}>
                  <Icon name="clock-outline" type="material-community" size={16} color="#666666" />
                  <Text style={styles.dateText}>Due: {formatDate(commitment.dueDate)}</Text>
                </View>

                <View style={styles.cardFooter}>
                  {commitment.relatedCommitments.length > 0 && (
                    <Button
                      title={showRelated === commitment.id ? "Hide Related" : "Show Related"}
                      type="clear"
                      size="sm"
                      icon={{
                        name: 'link-variant',
                        type: 'material-community',
                        size: 16,
                        color: '#4782DA'
                      }}
                      iconRight
                      titleStyle={styles.relatedButtonText}
                      onPress={() => setShowRelated(showRelated === commitment.id ? null : commitment.id)}
                    />
                  )}

                  <TouchableOpacity onPress={() => handleDelete(commitment.id)}>
                    <Icon name="trash-can-outline" type="material-community" size={20} color="#DA4747" />
                  </TouchableOpacity>
                </View>

                {showRelated === commitment.id && (
                  <View style={styles.relatedContainer}>
                    <Text style={styles.relatedTitle}>Related Commitments:</Text>
                    {getRelatedCommitments(commitment.id).map(related => (
                      <View key={related.id} style={styles.relatedItem}>
                        <View style={[styles.priorityDot, { backgroundColor: getPriorityColor(related.priority) }]} />
                        <Text style={styles.relatedText}>{related.text}</Text>
                      </View>
                    ))}
                  </View>
                )}
              </Card>
            </View>
          ))
        )}
      </ScrollView>

      <FAB
        icon={{ name: 'plus', type: 'material-community', color: 'white' }}
        placement="right"
        color="#4782DA"
        onPress={() => setShowDialog(true)}
      />

      <Overlay
        isVisible={showDialog}
        onBackdropPress={() => setShowDialog(false)}
        overlayStyle={styles.dialog}
      >
        <Text style={styles.dialogTitle}>Add New Commitment</Text>
        <TextInput
          style={styles.dialogInput}
          placeholder="Enter your commitment..."
          value={dialogText}
          onChangeText={setDialogText}
          multiline
          numberOfLines={4}
        />
        <View style={styles.dialogButtons}>
          <Button
            title="Cancel"
            type="outline"
            containerStyle={styles.dialogButton}
            onPress={() => setShowDialog(false)}
          />
          <Button
            title="Add"
            containerStyle={styles.dialogButton}
            onPress={handleAddCommitment}
            disabled={!dialogText.trim()}
          />
        </View>
      </Overlay>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  header: {
    padding: 15,
    backgroundColor: 'white',
    borderBottomWidth: 1,
    borderBottomColor: '#e0e0e0',
  },
  title: {
    fontSize: 20,
    fontWeight: 'bold',
    marginBottom: 10,
  },
  searchInput: {
    borderWidth: 1,
    borderColor: '#e0e0e0',
    borderRadius: 8,
    padding: 10,
    backgroundColor: '#f9f9f9',
  },
  filterContainer: {
    padding: 10,
    backgroundColor: 'white',
    borderBottomWidth: 1,
    borderBottomColor: '#e0e0e0',
  },
  chipContainer: {
    marginRight: 8,
  },
  activeChip: {
    backgroundColor: '#4782DA',
  },
  inactiveChip: {
    backgroundColor: 'transparent',
    borderColor: '#4782DA',
  },
  scrollContainer: {
    flex: 1,
    padding: 10,
  },
  card: {
    borderRadius: 10,
    padding: 15,
    marginBottom: 10,
  },
  cardHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 10,
  },
  titleContainer: {
    flex: 1,
  },
  priorityIndicator: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 5,
  },
  priorityDot: {
    width: 10,
    height: 10,
    borderRadius: 5,
    marginRight: 5,
  },
  priorityText: {
    fontSize: 14,
    fontWeight: '500',
  },
  sourceText: {
    fontSize: 12,
    color: '#666666',
  },
  checkbox: {
    padding: 0,
    margin: 0,
    marginLeft: 10,
    marginTop: -5,
  },
  commitmentText: {
    fontSize: 16,
    marginBottom: 10,
  },
  dateContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 10,
  },
  dateText: {
    fontSize: 14,
    color: '#666666',
    marginLeft: 5,
  },
  cardFooter: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginTop: 5,
  },
  relatedButtonText: {
    fontSize: 14,
    color: '#4782DA',
  },
  relatedContainer: {
    backgroundColor: '#f5f5f5',
    padding: 10,
    borderRadius: 8,
    marginTop: 10,
  },
  relatedTitle: {
    fontSize: 14,
    fontWeight: 'bold',
    marginBottom: 5,
  },
  relatedItem: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 8,
    backgroundColor: 'white',
    borderRadius: 6,
    marginBottom: 5,
  },
  relatedText: {
    fontSize: 14,
    flex: 1,
  },
  emptyState: {
    alignItems: 'center',
    justifyContent: 'center',
    padding: 40,
  },
  emptyText: {
    fontSize: 16,
    color: '#888888',
    marginTop: 10,
  },
  dialog: {
    width: '80%',
    borderRadius: 10,
    padding: 20,
  },
  dialogTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 15,
  },
  dialogInput: {
    borderWidth: 1,
    borderColor: '#e0e0e0',
    borderRadius: 8,
    padding: 10,
    minHeight: 100,
    textAlignVertical: 'top',
    marginBottom: 20,
  },
  dialogButtons: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  dialogButton: {
    width: '48%',
  },
});
