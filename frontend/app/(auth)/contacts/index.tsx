import React, { useState, useCallback } from 'react';

import { Text, Card, Input, useTheme, makeStyles } from '@rneui/themed';
import { View, ScrollView } from 'react-native';

import { LoadingSpinner } from '../../../components/Loading/LoadingSpinner';
import { AnimatedButton } from '../../../components/ui/AnimatedButton';
import { useToast } from '../../../components/ui/ToastProvider';
import { useAuth } from '../../../contexts/AuthContext';

interface Contact {
  id: string;
  name: string;
  email: string;
  phone?: string;
  lastContact?: string;
  nextReminder?: string;
  notes?: string;
  relationshipStrength: 1 | 2 | 3 | 4 | 5; // 1-5 scale
  tags: string[];
}

interface Reminder {
  id: string;
  contactId: string;
  date: string;
  type: 'CALL' | 'EMAIL' | 'MEET' | 'OTHER';
  notes?: string;
  completed: boolean;
}

export default function ContactsScreen() {
  const { theme } = useTheme();
  const styles = useStyles();
  const { user } = useAuth();
  const { showToast } = useToast();
  const [loading, setLoading] = useState(false);
  const [contacts, setContacts] = useState<Contact[]>([]);
  const [reminders, setReminders] = useState<Reminder[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [showAddContact, setShowAddContact] = useState(false);
  const [newContact, setNewContact] = useState({
    name: '',
    email: '',
    phone: '',
    notes: '',
    relationshipStrength: 3,
    tags: [],
  });

  const handleAddContact = useCallback(async () => {
    if (!newContact.name || !newContact.email) {
      showToast({
        type: 'error',
        message: 'Name and email are required',
        duration: 3000,
      });
      return;
    }

    setLoading(true);
    try {
      // TODO: Implement API call to add contact
      showToast({
        type: 'success',
        message: 'Contact added successfully',
        duration: 3000,
      });
      setShowAddContact(false);
      setNewContact({
        name: '',
        email: '',
        phone: '',
        notes: '',
        relationshipStrength: 3,
        tags: [],
      });
    } catch (error) {
      showToast({
        type: 'error',
        message: 'Failed to add contact',
        duration: 3000,
      });
    } finally {
      setLoading(false);
    }
  }, [newContact, showToast]);

  const handleSetReminder = useCallback(async (contactId: string, date: string, type: Reminder['type']) => {
    setLoading(true);
    try {
      // TODO: Implement API call to set reminder
      showToast({
        type: 'success',
        message: 'Reminder set successfully',
        duration: 3000,
      });
    } catch (error) {
      showToast({
        type: 'error',
        message: 'Failed to set reminder',
        duration: 3000,
      });
    } finally {
      setLoading(false);
    }
  }, [showToast]);

  if (!user) {
    return <LoadingSpinner fullScreen text="Loading..." />;
  }

  return (
    <ScrollView style={styles.container}>
      <View style={styles.header}>
        <Text h4 style={styles.title}>Contact Management</Text>
        <AnimatedButton
          title="Add Contact"
          onPress={() => setShowAddContact(true)}
          scaleOnPress
          containerStyle={styles.addButton}
        />
      </View>

      <Input
        placeholder="Search contacts..."
        value={searchQuery}
        onChangeText={setSearchQuery}
        containerStyle={styles.searchInput}
        leftIcon={{ type: 'font-awesome', name: 'search', color: theme.colors.grey3 }}
      />

      {showAddContact && (
        <Card containerStyle={styles.card}>
          <Card.Title>Add New Contact</Card.Title>
          <Input
            placeholder="Name"
            value={newContact.name}
            onChangeText={(text) => setNewContact(prev => ({ ...prev, name: text }))}
          />
          <Input
            placeholder="Email"
            value={newContact.email}
            onChangeText={(text) => setNewContact(prev => ({ ...prev, email: text }))}
            keyboardType="email-address"
          />
          <Input
            placeholder="Phone"
            value={newContact.phone}
            onChangeText={(text) => setNewContact(prev => ({ ...prev, phone: text }))}
            keyboardType="phone-pad"
          />
          <Input
            placeholder="Notes"
            value={newContact.notes}
            onChangeText={(text) => setNewContact(prev => ({ ...prev, notes: text }))}
            multiline
            numberOfLines={3}
          />
          <AnimatedButton
            title={loading ? "Adding..." : "Save Contact"}
            onPress={handleAddContact}
            loading={loading}
            disabled={loading || !newContact.name || !newContact.email}
            scaleOnPress
            containerStyle={styles.button}
          />
        </Card>
      )}

      <Card containerStyle={styles.card}>
        <Card.Title>Upcoming Reminders</Card.Title>
        {reminders.length > 0 ? (
          reminders.map((reminder) => (
            <View key={reminder.id} style={styles.reminderItem}>
              <Text>{reminder.type}</Text>
              <Text>{new Date(reminder.date).toLocaleDateString()}</Text>
              <AnimatedButton
                title="Complete"
                onPress={() => {/* TODO: Implement complete reminder */}}
                size="sm"
                scaleOnPress
              />
            </View>
          ))
        ) : (
          <Text style={styles.emptyText}>No upcoming reminders</Text>
        )}
      </Card>

      <Card containerStyle={styles.card}>
        <Card.Title>Contacts</Card.Title>
        {contacts.length > 0 ? (
          contacts.map((contact) => (
            <View key={contact.id} style={styles.contactItem}>
              <View style={styles.contactInfo}>
                <Text style={styles.contactName}>{contact.name}</Text>
                <Text style={styles.contactDetails}>{contact.email}</Text>
                {contact.lastContact && (
                  <Text style={styles.contactDetails}>
                    Last Contact: {new Date(contact.lastContact).toLocaleDateString()}
                  </Text>
                )}
              </View>
              <View style={styles.contactActions}>
                <AnimatedButton
                  title="Set Reminder"
                  onPress={() => {/* TODO: Implement set reminder modal */}}
                  size="sm"
                  scaleOnPress
                />
                <AnimatedButton
                  title="Contact"
                  onPress={() => {/* TODO: Implement contact actions modal */}}
                  size="sm"
                  scaleOnPress
                />
              </View>
            </View>
          ))
        ) : (
          <Text style={styles.emptyText}>No contacts yet</Text>
        )}
      </Card>
    </ScrollView>
  );
}

const useStyles = makeStyles((theme) => ({
  container: {
    flex: 1,
    backgroundColor: theme.colors.background,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: theme.spacing.md,
  },
  title: {
    color: theme.colors.grey0,
  },
  addButton: {
    borderRadius: theme.borderRadius.sm,
    overflow: 'hidden',
  },
  searchInput: {
    paddingHorizontal: theme.spacing.md,
    marginBottom: theme.spacing.sm,
  },
  card: {
    borderRadius: theme.borderRadius.md,
    marginBottom: theme.spacing.md,
  },
  button: {
    marginTop: theme.spacing.sm,
    borderRadius: theme.borderRadius.sm,
    overflow: 'hidden',
  },
  reminderItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: theme.spacing.sm,
    borderBottomWidth: 1,
    borderBottomColor: theme.colors.grey5,
  },
  contactItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: theme.spacing.md,
    borderBottomWidth: 1,
    borderBottomColor: theme.colors.grey5,
  },
  contactInfo: {
    flex: 1,
  },
  contactName: {
    fontSize: theme.fontSize.md,
    fontWeight: 'bold',
    color: theme.colors.grey0,
  },
  contactDetails: {
    fontSize: theme.fontSize.sm,
    color: theme.colors.grey2,
  },
  contactActions: {
    flexDirection: 'row',
    gap: theme.spacing.sm,
  },
  emptyText: {
    textAlign: 'center',
    color: theme.colors.grey3,
    padding: theme.spacing.md,
  },
})); 