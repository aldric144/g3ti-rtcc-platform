/**
 * G3TI RTCC Mobile App - Message Bubble Component
 */

import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import type { MobileMessage } from '../types';

interface MessageBubbleProps {
  message: MobileMessage;
  isOwn: boolean;
}

export const MessageBubble: React.FC<MessageBubbleProps> = ({ message, isOwn }) => {
  return (
    <View style={[styles.container, isOwn ? styles.ownContainer : styles.otherContainer]}>
      {!isOwn && (
        <View style={styles.header}>
          <Text style={styles.senderName}>{message.sender_name}</Text>
          {message.is_rtcc && (
            <View style={styles.rtccBadge}>
              <Text style={styles.rtccText}>RTCC</Text>
            </View>
          )}
        </View>
      )}
      <View style={[styles.bubble, isOwn ? styles.ownBubble : styles.otherBubble]}>
        <Text style={styles.content}>{message.content}</Text>
      </View>
      <View style={[styles.footer, isOwn && styles.ownFooter]}>
        <Text style={styles.time}>
          {new Date(message.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
        </Text>
        {isOwn && message.read && (
          <Ionicons name="checkmark-done" size={14} color="#3b82f6" style={styles.readIcon} />
        )}
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    marginVertical: 4,
    marginHorizontal: 8,
    maxWidth: '80%',
  },
  ownContainer: {
    alignSelf: 'flex-end',
  },
  otherContainer: {
    alignSelf: 'flex-start',
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 2,
  },
  senderName: {
    color: '#9ca3af',
    fontSize: 12,
    fontWeight: '500',
  },
  rtccBadge: {
    backgroundColor: '#3b82f6',
    paddingHorizontal: 4,
    paddingVertical: 1,
    borderRadius: 3,
    marginLeft: 6,
  },
  rtccText: {
    color: '#fff',
    fontSize: 9,
    fontWeight: '700',
  },
  bubble: {
    padding: 10,
    borderRadius: 16,
  },
  ownBubble: {
    backgroundColor: '#3b82f6',
    borderBottomRightRadius: 4,
  },
  otherBubble: {
    backgroundColor: '#374151',
    borderBottomLeftRadius: 4,
  },
  content: {
    color: '#fff',
    fontSize: 15,
  },
  footer: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: 2,
  },
  ownFooter: {
    justifyContent: 'flex-end',
  },
  time: {
    color: '#6b7280',
    fontSize: 11,
  },
  readIcon: {
    marginLeft: 4,
  },
});
