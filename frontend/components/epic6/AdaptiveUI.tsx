import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, ScrollView, Switch, TouchableOpacity, Animated } from 'react-native';
import { Card, Button, Icon, Slider, Divider, Badge } from '@rneui/themed';
import { Dimensions } from 'react-native';
import { useFocusEffect } from '@react-navigation/native';

interface UiPreference {
  id: string;
  name: string;
  description: string;
  value: boolean | number | string;
  type: 'toggle' | 'slider' | 'select';
  options?: string[];
  min?: number;
  max?: number;
  step?: number;
}

interface AchievementItem {
  id: string;
  title: string;
  description: string;
  icon: string;
  progress: number;
  isUnlocked: boolean;
  points: number;
  category: 'productivity' | 'consistency' | 'focus' | 'learning';
}

export const AdaptiveUI = () => {
  const [activeTab, setActiveTab] = useState<'preferences' | 'gamification'>('preferences');
  const [uiPreferences, setUiPreferences] = useState<UiPreference[]>([
    {
      id: 'reduce_motion',
      name: 'Reduce Motion',
      description: 'Limit animations and motion effects',
      value: false,
      type: 'toggle'
    },
    {
      id: 'high_contrast',
      name: 'High Contrast',
      description: 'Enhance color contrast for better visibility',
      value: false,
      type: 'toggle'
    },
    {
      id: 'font_size',
      name: 'Font Size',
      description: 'Adjust text size throughout the app',
      value: 1,
      type: 'slider',
      min: 0.8,
      max: 1.4,
      step: 0.1
    },
    {
      id: 'color_theme',
      name: 'Color Theme',
      description: 'Choose a color scheme that works best for you',
      value: 'default',
      type: 'select',
      options: ['default', 'calm', 'focus', 'warm', 'cool']
    },
    {
      id: 'focus_mode',
      name: 'Focus Mode',
      description: 'Reduce on-screen distractions when enabled',
      value: false,
      type: 'toggle'
    },
    {
      id: 'notification_style',
      name: 'Notification Style',
      description: 'Choose how notifications appear',
      value: 'standard',
      type: 'select',
      options: ['standard', 'minimal', 'detailed', 'none']
    },
    {
      id: 'reading_guide',
      name: 'Reading Guide',
      description: 'Add a focus line when reading long text',
      value: false,
      type: 'toggle'
    }
  ]);
  
  const [achievements, setAchievements] = useState<AchievementItem[]>([
    {
      id: '1',
      title: 'Task Master',
      description: 'Complete 50 tasks',
      icon: 'checkbox-marked-circle',
      progress: 38,
      isUnlocked: false,
      points: 100,
      category: 'productivity'
    },
    {
      id: '2',
      title: 'Focus Champion',
      description: 'Maintain focus mode for 10 hours total',
      icon: 'timer-outline',
      progress: 100,
      isUnlocked: true,
      points: 150,
      category: 'focus'
    },
    {
      id: '3',
      title: 'Consistency Streak',
      description: 'Use the app for 7 consecutive days',
      icon: 'calendar-check',
      progress: 71,
      isUnlocked: false,
      points: 75,
      category: 'consistency'
    },
    {
      id: '4',
      title: 'Planning Expert',
      description: 'Schedule 25 tasks with appropriate time blocks',
      icon: 'calendar-clock',
      progress: 60,
      isUnlocked: false,
      points: 100,
      category: 'productivity'
    },
    {
      id: '5',
      title: 'Reflection Master',
      description: 'Complete 10 daily reflections',
      icon: 'thought-bubble',
      progress: 40,
      isUnlocked: false,
      points: 75,
      category: 'learning'
    }
  ]);
  
  const [motivationProfile, setMotivationProfile] = useState({
    achievement: 80,
    social: 35,
    mastery: 65,
    progression: 70
  });

  const [scale] = useState(new Animated.Value(1));
  const [rewardPoints, setRewardPoints] = useState(0);
  const [showReward, setShowReward] = useState(false);
  
  useEffect(() => {
    const storedPreferences = {
      reduce_motion: false,
      high_contrast: false,
      font_size: 1,
      color_theme: 'default',
      focus_mode: false,
      notification_style: 'standard',
      reading_guide: false
    };
    
    // Apply stored preferences (mock)
    setUiPreferences(prev => prev.map(pref => ({
      ...pref,
      value: storedPreferences[pref.id as keyof typeof storedPreferences] ?? pref.value
    })));
  }, []);
  
  // Simulate focus rewards
  useFocusEffect(
    React.useCallback(() => {
      if (activeTab === 'gamification') {
        setTimeout(() => {
          addRewardPoints(10);
        }, 1000);
      }
      return () => {};
    }, [activeTab])
  );
  
  const handlePreferenceChange = (id: string, value: boolean | number | string) => {
    setUiPreferences(prev => 
      prev.map(pref => pref.id === id ? { ...pref, value } : pref)
    );
    
    // In a real app, save to storage and apply changes
    if (id === 'reduce_motion' && typeof value === 'boolean' && value) {
      addRewardPoints(5); // Reward for using accessibility features
    }
  };
  
  const addRewardPoints = (points: number) => {
    setRewardPoints(points);
    setShowReward(true);
    
    Animated.sequence([
      Animated.timing(scale, {
        toValue: 1.2,
        duration: 200,
        useNativeDriver: true
      }),
      Animated.timing(scale, {
        toValue: 1,
        duration: 200,
        useNativeDriver: true
      })
    ]).start();
    
    setTimeout(() => {
      setShowReward(false);
    }, 2000);
  };
  
  const getProgressColor = (progress: number) => {
    if (progress < 33) return '#DA4747';
    if (progress < 66) return '#DAA147';
    return '#47DA96';
  };

  const getColorThemeMainColor = (theme: string) => {
    switch (theme) {
      case 'calm': return '#80DEEA';
      case 'focus': return '#9FA8DA';
      case 'warm': return '#FFCC80';
      case 'cool': return '#80CBC4';
      default: return '#90CAF9';
    }
  };
  
  const renderPreferenceControl = (preference: UiPreference) => {
    switch (preference.type) {
      case 'toggle':
        return (
          <Switch
            value={preference.value as boolean}
            onValueChange={(value) => handlePreferenceChange(preference.id, value)}
            trackColor={{ false: '#e0e0e0', true: '#4782DA' }}
            thumbColor={preference.value ? '#ffffff' : '#f5f5f5'}
          />
        );
      
      case 'slider':
        return (
          <View style={styles.sliderContainer}>
            <Text style={styles.sliderValue}>
              {preference.id === 'font_size' ? `${(preference.value as number).toFixed(1)}x` : preference.value}
            </Text>
            <Slider
              value={preference.value as number}
              onValueChange={(value) => handlePreferenceChange(preference.id, value)}
              minimumValue={preference.min}
              maximumValue={preference.max}
              step={preference.step}
              thumbStyle={styles.sliderThumb}
              thumbTintColor="#4782DA"
              minimumTrackTintColor="#4782DA"
              maximumTrackTintColor="#e0e0e0"
              style={styles.slider}
            />
          </View>
        );
      
      case 'select':
        return (
          <View style={styles.optionsContainer}>
            {preference.options?.map((option) => (
              <TouchableOpacity
                key={option}
                style={[
                  styles.optionButton,
                  preference.value === option && styles.selectedOption,
                  preference.id === 'color_theme' && {
                    overflow: 'hidden',
                    padding: 0
                  }
                ]}
                onPress={() => handlePreferenceChange(preference.id, option)}
              >
                {preference.id === 'color_theme' ? (
                  <View
                    style={[
                      styles.themePreview,
                      { backgroundColor: getColorThemeMainColor(option) },
                      preference.value === option && styles.selectedThemePreview
                    ]}
                  >
                    <Text style={styles.themeText}>
                      {option.charAt(0).toUpperCase() + option.slice(1)}
                    </Text>
                  </View>
                ) : (
                  <Text
                    style={[
                      styles.optionText,
                      preference.value === option && styles.selectedOptionText
                    ]}
                  >
                    {option.charAt(0).toUpperCase() + option.slice(1)}
                  </Text>
                )}
              </TouchableOpacity>
            ))}
          </View>
        );
      
      default:
        return null;
    }
  };
  
  return (
    <View style={styles.container}>
      <View style={styles.tabContainer}>
        <TouchableOpacity
          style={[styles.tab, activeTab === 'preferences' && styles.activeTab]}
          onPress={() => setActiveTab('preferences')}
        >
          <Icon
            name="tune"
            type="material"
            size={24}
            color={activeTab === 'preferences' ? '#4782DA' : '#666666'}
          />
          <Text style={[
            styles.tabText,
            activeTab === 'preferences' && styles.activeTabText
          ]}>
            UI Preferences
          </Text>
        </TouchableOpacity>
        
        <TouchableOpacity
          style={[styles.tab, activeTab === 'gamification' && styles.activeTab]}
          onPress={() => setActiveTab('gamification')}
        >
          <Icon
            name="trophy"
            type="material-community"
            size={24}
            color={activeTab === 'gamification' ? '#4782DA' : '#666666'}
          />
          <Text style={[
            styles.tabText,
            activeTab === 'gamification' && styles.activeTabText
          ]}>
            Achievements
          </Text>
        </TouchableOpacity>
      </View>
      
      {showReward && (
        <Animated.View 
          style={[
            styles.rewardContainer,
            { transform: [{ scale }] }
          ]}
        >
          <Text style={styles.rewardText}>+{rewardPoints} points</Text>
        </Animated.View>
      )}
      
      <ScrollView style={styles.scrollContainer}>
        {activeTab === 'preferences' ? (
          <>
            <Card containerStyle={styles.card}>
              <Card.Title>Neurodiverse-Optimized UI</Card.Title>
              <Text style={styles.subtitle}>
                Customize your app experience to match your needs and preferences.
              </Text>
              
              {uiPreferences.map((preference) => (
                <View key={preference.id} style={styles.preferenceItem}>
                  <View style={styles.preferenceInfo}>
                    <Text style={styles.preferenceName}>{preference.name}</Text>
                    <Text style={styles.preferenceDescription}>{preference.description}</Text>
                  </View>
                  <View style={styles.preferenceControl}>
                    {renderPreferenceControl(preference)}
                  </View>
                </View>
              ))}
            </Card>
            
            <Card containerStyle={styles.card}>
              <Card.Title>Current Energy Level</Card.Title>
              <Text style={styles.subtitle}>
                The UI will adapt to your energy level throughout the day.
              </Text>
              
              <View style={styles.energyLevelContainer}>
                <TouchableOpacity 
                  style={[styles.energyButton, styles.energyButtonLow]}
                  onPress={() => {
                    // Apply low energy UI adaptations
                    handlePreferenceChange('reduce_motion', true);
                  }}
                >
                  <Icon name="battery-low" type="material-community" color="white" size={24} />
                  <Text style={styles.energyButtonText}>Low</Text>
                </TouchableOpacity>
                
                <TouchableOpacity 
                  style={[styles.energyButton, styles.energyButtonMedium]}
                  onPress={() => {
                    // Apply medium energy UI adaptations
                    handlePreferenceChange('reduce_motion', false);
                    handlePreferenceChange('color_theme', 'calm');
                  }}
                >
                  <Icon name="battery-medium" type="material-community" color="white" size={24} />
                  <Text style={styles.energyButtonText}>Medium</Text>
                </TouchableOpacity>
                
                <TouchableOpacity 
                  style={[styles.energyButton, styles.energyButtonHigh]}
                  onPress={() => {
                    // Apply high energy UI adaptations
                    handlePreferenceChange('reduce_motion', false);
                    handlePreferenceChange('color_theme', 'focus');
                  }}
                >
                  <Icon name="battery-high" type="material-community" color="white" size={24} />
                  <Text style={styles.energyButtonText}>High</Text>
                </TouchableOpacity>
              </View>
              
              <Text style={styles.energyExplanation}>
                Select your current energy level to optimize the interface.
                Low energy settings reduce visual stimulation, while high energy
                settings provide more engaging interactions.
              </Text>
            </Card>
          </>
        ) : (
          <>
            <Card containerStyle={styles.card}>
              <View style={styles.cardHeader}>
                <Card.Title>Your Motivation Profile</Card.Title>
                <Badge
                  value="Level 5"
                  containerStyle={{}}
                  badgeStyle={styles.levelBadge}
                  textStyle={styles.levelBadgeText}
                />
              </View>
              
              <Text style={styles.subtitle}>
                Your personal rewards are tailored to your motivation style.
              </Text>
              
              <View style={styles.motivationContainer}>
                <View style={styles.motivationItem}>
                  <View style={styles.motivationBarContainer}>
                    <View 
                      style={[
                        styles.motivationBar, 
                        { height: `${motivationProfile.achievement}%`, backgroundColor: '#4782DA' }
                      ]} 
                    />
                  </View>
                  <Text style={styles.motivationLabel}>Achievement</Text>
                </View>
                
                <View style={styles.motivationItem}>
                  <View style={styles.motivationBarContainer}>
                    <View 
                      style={[
                        styles.motivationBar, 
                        { height: `${motivationProfile.social}%`, backgroundColor: '#DA9647' }
                      ]} 
                    />
                  </View>
                  <Text style={styles.motivationLabel}>Social</Text>
                </View>
                
                <View style={styles.motivationItem}>
                  <View style={styles.motivationBarContainer}>
                    <View 
                      style={[
                        styles.motivationBar, 
                        { height: `${motivationProfile.mastery}%`, backgroundColor: '#8047DA' }
                      ]} 
                    />
                  </View>
                  <Text style={styles.motivationLabel}>Mastery</Text>
                </View>
                
                <View style={styles.motivationItem}>
                  <View style={styles.motivationBarContainer}>
                    <View 
                      style={[
                        styles.motivationBar, 
                        { height: `${motivationProfile.progression}%`, backgroundColor: '#47DA96' }
                      ]} 
                    />
                  </View>
                  <Text style={styles.motivationLabel}>Progression</Text>
                </View>
              </View>
              
              <Text style={styles.motivationExplanation}>
                Your primary motivators are Achievement and Progression.
                We'll focus on milestone tracking and visible progress indicators.
              </Text>
            </Card>
            
            <Card containerStyle={styles.card}>
              <Card.Title>Your Achievements</Card.Title>
              <Text style={styles.subtitle}>
                Track your progress and earn rewards for using the app effectively.
              </Text>
              
              {achievements.map((achievement) => (
                <View 
                  key={achievement.id} 
                  style={[
                    styles.achievementItem,
                    achievement.isUnlocked && styles.unlockedAchievement
                  ]}
                >
                  <View style={styles.achievementIconContainer}>
                    <Icon
                      name={achievement.icon}
                      type="material-community"
                      color={achievement.isUnlocked ? '#47DA96' : '#888888'}
                      size={28}
                    />
                  </View>
                  
                  <View style={styles.achievementContent}>
                    <View style={styles.achievementHeader}>
                      <Text style={styles.achievementTitle}>{achievement.title}</Text>
                      <Text style={styles.achievementPoints}>+{achievement.points}</Text>
                    </View>
                    
                    <Text style={styles.achievementDescription}>{achievement.description}</Text>
                    
                    <View style={styles.progressContainer}>
                      <View style={styles.progressBar}>
                        <View 
                          style={[
                            styles.progressFill,
                            { width: `${achievement.progress}%`, backgroundColor: getProgressColor(achievement.progress) }
                          ]} 
                        />
                      </View>
                      <Text style={styles.progressText}>{achievement.progress}%</Text>
                    </View>
                  </View>
                </View>
              ))}
              
              <Button
                title="View All Achievements"
                type="outline"
                buttonStyle={styles.viewAllButton}
                containerStyle={styles.viewAllButtonContainer}
              />
            </Card>
          </>
        )}
      </ScrollView>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  tabContainer: {
    flexDirection: 'row',
    backgroundColor: 'white',
    paddingVertical: 10,
    paddingHorizontal: 10,
    borderBottomWidth: 1,
    borderBottomColor: '#e0e0e0',
  },
  tab: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 10,
    borderRadius: 8,
  },
  activeTab: {
    backgroundColor: '#EBF2FF',
  },
  tabText: {
    marginLeft: 6,
    fontSize: 14,
    color: '#666666',
  },
  activeTabText: {
    color: '#4782DA',
    fontWeight: 'bold',
  },
  scrollContainer: {
    flex: 1,
    padding: 10,
  },
  card: {
    borderRadius: 10,
    marginBottom: 15,
    padding: 15,
  },
  subtitle: {
    fontSize: 14,
    textAlign: 'center',
    marginBottom: 15,
    color: '#666666',
  },
  preferenceItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 20,
    paddingBottom: 15,
    borderBottomWidth: 1,
    borderBottomColor: '#f0f0f0',
  },
  preferenceInfo: {
    flex: 1,
    paddingRight: 15,
  },
  preferenceName: {
    fontSize: 16,
    fontWeight: 'bold',
    marginBottom: 4,
  },
  preferenceDescription: {
    fontSize: 14,
    color: '#666666',
  },
  preferenceControl: {
    minWidth: 60,
    alignItems: 'flex-end',
  },
  sliderContainer: {
    width: 150,
    alignItems: 'center',
  },
  slider: {
    width: '100%',
  },
  sliderThumb: {
    width: 20,
    height: 20,
    borderRadius: 10,
  },
  sliderValue: {
    fontSize: 14,
    fontWeight: 'bold',
    marginBottom: 5,
  },
  optionsContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'flex-end',
  },
  optionButton: {
    backgroundColor: '#f0f0f0',
    paddingHorizontal: 12,
    paddingVertical: 8,
    borderRadius: 20,
    marginLeft: 8,
    marginBottom: 8,
  },
  selectedOption: {
    backgroundColor: '#4782DA',
  },
  optionText: {
    fontSize: 14,
    color: '#666666',
  },
  selectedOptionText: {
    color: 'white',
  },
  themePreview: {
    paddingHorizontal: 12,
    paddingVertical: 8,
    borderRadius: 20,
    height: '100%',
    width: '100%',
    alignItems: 'center',
    justifyContent: 'center',
  },
  selectedThemePreview: {
    borderWidth: 2,
    borderColor: '#4782DA',
  },
  themeText: {
    fontSize: 12,
    color: '#333333',
    fontWeight: 'bold',
  },
  rewardContainer: {
    position: 'absolute',
    top: 80,
    alignSelf: 'center',
    backgroundColor: '#4782DA',
    paddingHorizontal: 15,
    paddingVertical: 10,
    borderRadius: 25,
    zIndex: 1000,
  },
  rewardText: {
    color: 'white',
    fontWeight: 'bold',
    fontSize: 16,
  },
  energyLevelContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 15,
  },
  energyButton: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 12,
    borderRadius: 8,
    marginHorizontal: 5,
  },
  energyButtonLow: {
    backgroundColor: '#DA4747',
  },
  energyButtonMedium: {
    backgroundColor: '#DAA147',
  },
  energyButtonHigh: {
    backgroundColor: '#47DA96',
  },
  energyButtonText: {
    color: 'white',
    fontWeight: 'bold',
    marginLeft: 5,
  },
  energyExplanation: {
    fontSize: 14,
    fontStyle: 'italic',
    color: '#666666',
    textAlign: 'center',
  },
  cardHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 10,
  },
  levelBadge: {
    backgroundColor: '#8047DA',
    paddingHorizontal: 8,
    borderRadius: 20,
  },
  levelBadgeText: {
    fontSize: 12,
    fontWeight: 'bold',
  },
  motivationContainer: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    marginVertical: 20,
    height: 150,
  },
  motivationItem: {
    alignItems: 'center',
  },
  motivationBarContainer: {
    width: 30,
    height: 120,
    backgroundColor: '#e0e0e0',
    borderRadius: 15,
    overflow: 'hidden',
    justifyContent: 'flex-end',
  },
  motivationBar: {
    width: '100%',
    borderTopLeftRadius: 15,
    borderTopRightRadius: 15,
  },
  motivationLabel: {
    fontSize: 12,
    marginTop: 5,
  },
  motivationExplanation: {
    fontSize: 14,
    fontStyle: 'italic',
    color: '#666666',
    textAlign: 'center',
    backgroundColor: '#f8f8f8',
    padding: 10,
    borderRadius: 8,
  },
  achievementItem: {
    flexDirection: 'row',
    backgroundColor: '#f8f8f8',
    borderRadius: 8,
    padding: 12,
    marginBottom: 15,
  },
  unlockedAchievement: {
    backgroundColor: '#f0fff5',
    borderLeftWidth: 3,
    borderLeftColor: '#47DA96',
  },
  achievementIconContainer: {
    marginRight: 15,
    paddingTop: 5,
  },
  achievementContent: {
    flex: 1,
  },
  achievementHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 5,
  },
  achievementTitle: {
    fontSize: 16,
    fontWeight: 'bold',
  },
  achievementPoints: {
    fontSize: 14,
    fontWeight: 'bold',
    color: '#4782DA',
  },
  achievementDescription: {
    fontSize: 14,
    color: '#666666',
    marginBottom: 10,
  },
  progressContainer: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  progressBar: {
    flex: 1,
    height: 8,
    backgroundColor: '#e0e0e0',
    borderRadius: 4,
    marginRight: 10,
    overflow: 'hidden',
  },
  progressFill: {
    height: '100%',
  },
  progressText: {
    fontSize: 12,
    fontWeight: 'bold',
    width: 40,
    textAlign: 'right',
  },
  viewAllButton: {
    borderColor: '#4782DA',
    borderRadius: 20,
  },
  viewAllButtonContainer: {
    marginTop: 5,
  },
}); 