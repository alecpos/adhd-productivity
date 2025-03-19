import React, { useState } from 'react';

import { Card, Button, Icon, Overlay } from '@rneui/themed';
import { View, Text, StyleSheet, ScrollView, Dimensions } from 'react-native';

import { LineChart } from 'react-native-chart-kit';

import { useAccessibilityPreferences } from '../../hooks/useAccessibilityPreferences';
import { useTheme } from '../../theme';

interface PatternData {
  labels: string[];
  datasets: {
    data: number[];
    color?: (opacity: number) => string;
    strokeWidth?: number;
  }[];
  legend?: string[];
}

interface ProductivityInsight {
  id: string;
  title: string;
  description: string;
  confidence: number;
  source: string;
  createdAt: string;
}

const mockPatternData: PatternData = {
  labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
  datasets: [
    {
      data: [65, 72, 84, 68, 78, 55, 60],
      color: (opacity = 1) => `rgba(71, 130, 218, ${opacity})`,
      strokeWidth: 2,
    }
  ],
  legend: ['Productivity']
};

const mockInsights: ProductivityInsight[] = [
  {
    id: '1',
    title: 'Productivity Peak: Wednesday',
    description: 'You consistently complete more tasks on Wednesdays than any other day of the week.',
    confidence: 0.89,
    source: 'LSTM Analysis',
    createdAt: '2023-03-01'
  },
  {
    id: '2',
    title: 'Energy Drop: Evening',
    description: 'Your task completion rate significantly decreases after 7PM.',
    confidence: 0.92,
    source: 'Circadian Rhythm Model',
    createdAt: '2023-03-02'
  },
  {
    id: '3',
    title: 'Focus Correlation',
    description: 'Tasks completed in quiet environments have 34% higher success rate.',
    confidence: 0.78,
    source: 'Feature Correlation',
    createdAt: '2023-03-03'
  }
];

export const ProductivityPatternViewer = () => {
  const [activePattern, setActivePattern] = useState<'daily' | 'weekly' | 'monthly'>('weekly');
  const [showInsightModal, setShowInsightModal] = useState(false);
  const [selectedInsight, setSelectedInsight] = useState<ProductivityInsight | null>(null);
  const { theme } = useTheme();
  const { reduceMotion, highContrast } = useAccessibilityPreferences();
  
  const screenWidth = Dimensions.get('window').width - 40;

  const chartConfig = {
    backgroundGradientFrom: theme.colors.background,
    backgroundGradientTo: theme.colors.background,
    decimalPlaces: 0,
    color: (opacity = 1) => highContrast 
      ? `rgba(255, 255, 255, ${opacity})` 
      : `rgba(71, 130, 218, ${opacity})`,
    labelColor: (opacity = 1) => `rgba(${highContrast ? '255, 255, 255' : theme.dark ? '255, 255, 255' : '0, 0, 0'}, ${opacity})`,
    style: {
      borderRadius: 16,
    },
    propsForDots: {
      r: "6",
      strokeWidth: "2",
      stroke: theme.colors.primary
    }
  };

  const handleInsightPress = (insight: ProductivityInsight) => {
    setSelectedInsight(insight);
    setShowInsightModal(true);
  };

  return (
    <ScrollView style={styles.container}>
      <Card containerStyle={styles.patternCard}>
        <Card.Title>Productivity Patterns</Card.Title>
        <View style={styles.patternToggle}>
          <Button
            title="Daily"
            type={activePattern === 'daily' ? "solid" : "outline"}
            size="sm"
            onPress={() => setActivePattern('daily')}
            buttonStyle={{ borderRadius: 20 }}
            containerStyle={{ marginRight: 5 }}
          />
          <Button
            title="Weekly"
            type={activePattern === 'weekly' ? "solid" : "outline"}
            size="sm"
            onPress={() => setActivePattern('weekly')}
            buttonStyle={{ borderRadius: 20 }}
            containerStyle={{ marginRight: 5 }}
          />
          <Button
            title="Monthly"
            type={activePattern === 'monthly' ? "solid" : "outline"}
            size="sm"
            onPress={() => setActivePattern('monthly')}
            buttonStyle={{ borderRadius: 20 }}
          />
        </View>
        
        <LineChart
          data={mockPatternData}
          width={screenWidth}
          height={220}
          chartConfig={chartConfig}
          bezier
          style={styles.chart}
          withDots={!reduceMotion}
          withInnerLines={!reduceMotion}
          withOuterLines={!reduceMotion}
          withShadow={!reduceMotion}
          withVerticalLabels={true}
          withHorizontalLabels={true}
        />
        
        <Text style={styles.patternExplanation}>
          Your productivity increases mid-week and drops on weekends. 
          This pattern is detected with 87% confidence based on your past 3 months of activity.
        </Text>
      </Card>
      
      <Card containerStyle={styles.insightsCard}>
        <Card.Title>Productivity Insights</Card.Title>
        
        {mockInsights.map((insight) => (
          <Card key={insight.id} containerStyle={styles.insightCard}>
            <View style={styles.insightHeader}>
              <View style={styles.titleContainer}>
                <Text style={styles.insightTitle}>{insight.title}</Text>
                <Text style={styles.insightSource}>{insight.source} • {Math.round(insight.confidence * 100)}% confidence</Text>
              </View>
              <Button
                type="clear"
                icon={<Icon name="info" size={20} color={theme.colors.primary} />}
                onPress={() => handleInsightPress(insight)}
              />
            </View>
            <Text style={styles.insightDescription}>{insight.description}</Text>
          </Card>
        ))}
      </Card>
      
      <Overlay
        isVisible={showInsightModal}
        onBackdropPress={() => setShowInsightModal(false)}
        overlayStyle={styles.modal}
      >
        {selectedInsight && (
          <View>
            <Text style={styles.modalTitle}>{selectedInsight.title}</Text>
            <Text style={styles.modalDescription}>{selectedInsight.description}</Text>
            <View style={styles.modalDetails}>
              <Text style={styles.modalLabel}>Source:</Text>
              <Text style={styles.modalValue}>{selectedInsight.source}</Text>
            </View>
            <View style={styles.modalDetails}>
              <Text style={styles.modalLabel}>Confidence:</Text>
              <Text style={styles.modalValue}>{Math.round(selectedInsight.confidence * 100)}%</Text>
            </View>
            <View style={styles.modalDetails}>
              <Text style={styles.modalLabel}>Generated:</Text>
              <Text style={styles.modalValue}>{selectedInsight.createdAt}</Text>
            </View>
            <Text style={styles.modalExplanation}>
              This insight was generated using the ProductivityPatternLSTM model analyzing your completed tasks over time.
              The model looks for recurring patterns in your productivity and correlates them with time of day, day of week, and other factors.
            </Text>
            <Button
              title="Close"
              onPress={() => setShowInsightModal(false)}
              buttonStyle={styles.closeButton}
            />
          </View>
        )}
      </Overlay>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    paddingHorizontal: 0,
  },
  patternCard: {
    borderRadius: 10,
    marginBottom: 10,
    padding: 15,
  },
  patternToggle: {
    flexDirection: 'row',
    justifyContent: 'center',
    marginBottom: 15,
  },
  chart: {
    marginVertical: 8,
    borderRadius: 16,
  },
  patternExplanation: {
    fontSize: 14,
    marginTop: 10,
    textAlign: 'center',
  },
  insightsCard: {
    borderRadius: 10,
    marginBottom: 20,
    padding: 10,
  },
  insightCard: {
    borderRadius: 8,
    marginBottom: 10,
    padding: 12,
  },
  insightHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 5,
  },
  titleContainer: {
    flex: 1,
  },
  insightTitle: {
    fontSize: 16,
    fontWeight: 'bold',
  },
  insightSource: {
    fontSize: 12,
    opacity: 0.7,
  },
  insightDescription: {
    fontSize: 14,
  },
  modal: {
    width: '80%',
    borderRadius: 10,
    padding: 20,
  },
  modalTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 10,
  },
  modalDescription: {
    fontSize: 16,
    marginBottom: 15,
  },
  modalDetails: {
    flexDirection: 'row',
    marginBottom: 5,
  },
  modalLabel: {
    fontWeight: 'bold',
    width: 100,
  },
  modalValue: {
    flex: 1,
  },
  modalExplanation: {
    fontSize: 14,
    marginTop: 15,
    marginBottom: 20,
    fontStyle: 'italic',
  },
  closeButton: {
    borderRadius: 10,
  },
}); 