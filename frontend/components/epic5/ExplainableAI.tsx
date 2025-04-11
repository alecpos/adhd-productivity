import React, { useState } from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity } from 'react-native';
import { Card, Button, Icon, Divider, BottomSheet, ListItem } from '@rneui/themed';
import { BarChart } from 'react-native-chart-kit';
import { Dimensions } from 'react-native';

interface FeatureImportance {
  feature: string;
  importance: number;
  description: string;
}

interface ModelExplanation {
  modelName: string;
  confidence: number;
  prediction: string;
  featureImportances: FeatureImportance[];
  counterfactuals: string[];
  datasetInfo: {
    size: number;
    demographics: string;
    lastUpdated: string;
  };
}

// Mock data for the explanations
const mockExplanation: ModelExplanation = {
  modelName: "ProductivityPredictor",
  confidence: 0.87,
  prediction: "High Productivity Time Block",
  featureImportances: [
    {
      feature: "Time of day",
      importance: 0.32,
      description: "Morning hours (9-11 AM) are historically your most productive time."
    },
    {
      feature: "Previous sleep duration",
      importance: 0.27,
      description: "You slept 7.5 hours last night, which is optimal for your productivity."
    },
    {
      feature: "Task complexity",
      importance: 0.18,
      description: "Current task has medium complexity based on your description."
    },
    {
      feature: "Environment",
      importance: 0.12,
      description: "Your current location (home office) has fewer distractions."
    },
    {
      feature: "Recent break time",
      importance: 0.11,
      description: "You took a 15-minute break 30 minutes ago."
    }
  ],
  counterfactuals: [
    "If you had slept less than 6 hours, productivity would likely be 'Medium'.",
    "If the task complexity was 'High', productivity would likely be 'Medium'.",
    "If the time was after 3 PM, productivity would likely be 'Medium'."
  ],
  datasetInfo: {
    size: 1245,
    demographics: "Balanced across age groups, genders, and neurotypes",
    lastUpdated: "2023-02-15"
  }
};

const mockSchedulingExplanation: ModelExplanation = {
  modelName: "ScheduleOptimizer",
  confidence: 0.82,
  prediction: "Optimal task placement at 10:00 AM",
  featureImportances: [
    {
      feature: "Historical performance",
      importance: 0.35,
      description: "You complete similar tasks 28% faster in the morning."
    },
    {
      feature: "Energy pattern",
      importance: 0.25,
      description: "Your energy level peaks around 10 AM based on past data."
    },
    {
      feature: "Task priority",
      importance: 0.20,
      description: "This is a high-priority task that benefits from high focus."
    },
    {
      feature: "Context switching",
      importance: 0.12,
      description: "Previous task is related, minimizing context switching."
    },
    {
      feature: "Break timing",
      importance: 0.08,
      description: "Scheduled after a short break for optimal focus."
    }
  ],
  counterfactuals: [
    "If this task had low priority, it would be scheduled in the afternoon.",
    "If your energy pattern showed afternoon peaks, it would be scheduled after lunch.",
    "If you had meetings in the morning, it would be scheduled at 2:00 PM."
  ],
  datasetInfo: {
    size: 892,
    demographics: "Trained with fairness objectives across different ADHD subtypes",
    lastUpdated: "2023-02-10"
  }
};

export const ExplainableAI = () => {
  const [activeExplanation, setActiveExplanation] = useState<'productivity' | 'scheduling'>('productivity');
  const [isBottomSheetVisible, setIsBottomSheetVisible] = useState(false);
  const [detailLevel, setDetailLevel] = useState<'simple' | 'detailed'>('simple');
  const [selectedFeature, setSelectedFeature] = useState<FeatureImportance | null>(null);

  const screenWidth = Dimensions.get('window').width - 40;

  const explanation = activeExplanation === 'productivity'
    ? mockExplanation
    : mockSchedulingExplanation;

  // Chart configuration
  const chartConfig = {
    backgroundGradientFrom: "#ffffff",
    backgroundGradientTo: "#ffffff",
    decimalPlaces: 2,
    color: (opacity = 1) => `rgba(71, 130, 218, ${opacity})`,
    labelColor: (opacity = 1) => `rgba(0, 0, 0, ${opacity})`,
    style: {
      borderRadius: 16,
    },
    barPercentage: 0.7,
  };

  // Format feature importance data for the chart
  const getFeatureImportanceData = () => {
    const labels = explanation.featureImportances.map(f => f.feature);
    const data = explanation.featureImportances.map(f => f.importance * 100);

    return {
      labels,
      datasets: [{ data }]
    };
  };

  const handleFeaturePress = (feature: FeatureImportance) => {
    setSelectedFeature(feature);
    setIsBottomSheetVisible(true);
  };

  const toggleDetailLevel = () => {
    setDetailLevel(detailLevel === 'simple' ? 'detailed' : 'simple');
  };

  return (
    <ScrollView style={styles.container}>
      <Card containerStyle={styles.card}>
        <Card.Title>Explainable AI</Card.Title>
        <Text style={styles.subtitle}>
          Understanding how our AI makes decisions in a transparent way.
        </Text>

        <View style={styles.toggleContainer}>
          <Button
            title="Productivity Prediction"
            type={activeExplanation === 'productivity' ? "solid" : "outline"}
            onPress={() => setActiveExplanation('productivity')}
            buttonStyle={[
              styles.toggleButton,
              activeExplanation === 'productivity' && styles.activeToggleButton
            ]}
            containerStyle={styles.toggleButtonContainer}
          />
          <Button
            title="Schedule Optimization"
            type={activeExplanation === 'scheduling' ? "solid" : "outline"}
            onPress={() => setActiveExplanation('scheduling')}
            buttonStyle={[
              styles.toggleButton,
              activeExplanation === 'scheduling' && styles.activeToggleButton
            ]}
            containerStyle={styles.toggleButtonContainer}
          />
        </View>
      </Card>

      <Card containerStyle={styles.card}>
        <View style={styles.predictionHeader}>
          <View>
            <Text style={styles.predictionTitle}>Prediction</Text>
            <Text style={styles.predictionText}>{explanation.prediction}</Text>
          </View>
          <View style={styles.confidenceContainer}>
            <Text style={styles.confidenceValue}>{Math.round(explanation.confidence * 100)}%</Text>
            <Text style={styles.confidenceLabel}>Confidence</Text>
          </View>
        </View>

        <Divider style={styles.divider} />

        <View style={styles.detailLevelContainer}>
          <Text style={styles.sectionTitle}>Explanation</Text>
          <Button
            title={detailLevel === 'detailed' ? "Simplify" : "More Details"}
            type="clear"
            onPress={toggleDetailLevel}
            titleStyle={styles.detailLevelButtonText}
            buttonStyle={styles.detailLevelButton}
            icon={{
              name: detailLevel === 'detailed' ? 'unfold-less-horizontal' : 'unfold-more-horizontal',
              type: 'material-community',
              size: 16,
              color: '#4782DA'
            }}
            iconRight
          />
        </View>

        {detailLevel === 'simple' ? (
          <Text style={styles.simplifiedExplanation}>
            This {activeExplanation === 'productivity' ? 'productivity prediction' : 'schedule optimization'} is
            primarily based on {explanation.featureImportances[0].feature.toLowerCase()} and
            {explanation.featureImportances[1].feature.toLowerCase()}.
            {explanation.featureImportances[0].description}
            {activeExplanation === 'productivity'
              ? "\n\nThe model analyzed your historical productivity patterns and current context to make this prediction."
              : "\n\nThe model analyzed your task characteristics and optimal scheduling patterns to make this recommendation."}
          </Text>
        ) : (
          <>
            <Text style={styles.detailedIntro}>
              The {explanation.modelName} model considered these factors (in order of importance):
            </Text>

            <BarChart
              data={getFeatureImportanceData()}
              width={screenWidth}
              height={220}
              chartConfig={chartConfig}
              style={styles.chart}
              fromZero
              showValuesOnTopOfBars
              withHorizontalLabels={false}
              segments={5}
            />

            <Text style={styles.tapHint}>Tap on any feature for more details</Text>

            {explanation.featureImportances.map((feature, index) => (
              <TouchableOpacity
                key={index}
                style={styles.featureItem}
                onPress={() => handleFeaturePress(feature)}
              >
                <View style={styles.featureHeaderContainer}>
                  <View style={styles.featureHeader}>
                    <Text style={styles.featureRank}>{index + 1}</Text>
                    <Text style={styles.featureName}>{feature.feature}</Text>
                  </View>
                  <Text style={styles.featureValue}>{Math.round(feature.importance * 100)}%</Text>
                </View>
                <View style={[styles.importanceBar, { width: `${feature.importance * 100}%` }]} />
              </TouchableOpacity>
            ))}

            <Divider style={styles.divider} />

            <Text style={styles.counterfactualTitle}>What would change the prediction?</Text>
            {explanation.counterfactuals.map((counterfactual, index) => (
              <View key={index} style={styles.counterfactualItem}>
                <Icon
                  name="shuffle-variant"
                  type="material-community"
                  color="#4782DA"
                  size={18}
                  containerStyle={styles.counterfactualIcon}
                />
                <Text style={styles.counterfactualText}>{counterfactual}</Text>
              </View>
            ))}

            <Divider style={styles.divider} />

            <View style={styles.datasetContainer}>
              <Text style={styles.datasetTitle}>About the Model</Text>
              <Text style={styles.datasetText}>
                This model was trained on {explanation.datasetInfo.size.toLocaleString()} data points.{'\n'}
                Demographics: {explanation.datasetInfo.demographics}{'\n'}
                Last updated: {explanation.datasetInfo.lastUpdated}
              </Text>
            </View>
          </>
        )}
      </Card>

      <BottomSheet
        isVisible={isBottomSheetVisible}
        onBackdropPress={() => setIsBottomSheetVisible(false)}
      >
        {selectedFeature && (
          <View style={styles.bottomSheetContainer}>
            <Text style={styles.bottomSheetTitle}>{selectedFeature.feature}</Text>
            <Text style={styles.bottomSheetImportance}>
              Importance: {Math.round(selectedFeature.importance * 100)}%
            </Text>
            <Text style={styles.bottomSheetDescription}>{selectedFeature.description}</Text>

            <Text style={styles.bottomSheetExplanation}>
              {selectedFeature.feature === 'Time of day'
                ? "This feature analyzes historical patterns of your productivity at different times of day. It compares your current time with these patterns to determine if it's likely to be a high-productivity period for you."
                : selectedFeature.feature === 'Energy pattern'
                ? "This feature uses your self-reported energy levels and biometric data (if available) to determine your current energy state. It compares this with the energy typically required for the task type."
                : "This feature considers the specific characteristics of the task and compares them with your historical performance on similar tasks. It helps the model understand if the current context is favorable for this task type."}
            </Text>

            <Button
              title="Close"
              onPress={() => setIsBottomSheetVisible(false)}
              buttonStyle={styles.closeButton}
            />
          </View>
        )}
      </BottomSheet>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
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
  toggleContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginTop: 5,
  },
  toggleButton: {
    borderRadius: 20,
    paddingHorizontal: 15,
  },
  activeToggleButton: {
    backgroundColor: '#4782DA',
  },
  toggleButtonContainer: {
    flex: 1,
    marginHorizontal: 5,
  },
  predictionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 15,
  },
  predictionTitle: {
    fontSize: 16,
    color: '#666666',
  },
  predictionText: {
    fontSize: 18,
    fontWeight: 'bold',
  },
  confidenceContainer: {
    alignItems: 'center',
    backgroundColor: '#f0f7ff',
    paddingHorizontal: 15,
    paddingVertical: 8,
    borderRadius: 20,
  },
  confidenceValue: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#4782DA',
  },
  confidenceLabel: {
    fontSize: 12,
    color: '#666666',
  },
  divider: {
    marginVertical: 15,
  },
  detailLevelContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 10,
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: 'bold',
  },
  detailLevelButton: {
    padding: 0,
  },
  detailLevelButtonText: {
    fontSize: 14,
    color: '#4782DA',
  },
  simplifiedExplanation: {
    fontSize: 16,
    lineHeight: 24,
    color: '#333333',
    marginBottom: 10,
  },
  detailedIntro: {
    fontSize: 16,
    marginBottom: 15,
  },
  chart: {
    marginVertical: 15,
    borderRadius: 8,
  },
  tapHint: {
    fontSize: 12,
    color: '#666666',
    textAlign: 'center',
    marginBottom: 15,
    fontStyle: 'italic',
  },
  featureItem: {
    marginBottom: 15,
  },
  featureHeaderContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 5,
  },
  featureHeader: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  featureRank: {
    width: 24,
    height: 24,
    borderRadius: 12,
    backgroundColor: '#4782DA',
    color: 'white',
    textAlign: 'center',
    lineHeight: 24,
    marginRight: 10,
    fontSize: 14,
    fontWeight: 'bold',
  },
  featureName: {
    fontSize: 16,
    fontWeight: '500',
  },
  featureValue: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#4782DA',
  },
  importanceBar: {
    height: 6,
    backgroundColor: '#4782DA',
    borderRadius: 3,
    marginTop: 5,
  },
  counterfactualTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    marginBottom: 15,
  },
  counterfactualItem: {
    flexDirection: 'row',
    marginBottom: 10,
    alignItems: 'flex-start',
  },
  counterfactualIcon: {
    marginRight: 10,
    marginTop: 2,
  },
  counterfactualText: {
    fontSize: 14,
    flex: 1,
    color: '#333333',
  },
  datasetContainer: {
    backgroundColor: '#f8f8f8',
    padding: 15,
    borderRadius: 8,
  },
  datasetTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    marginBottom: 10,
  },
  datasetText: {
    fontSize: 14,
    lineHeight: 20,
    color: '#666666',
  },
  bottomSheetContainer: {
    backgroundColor: 'white',
    padding: 20,
    borderTopLeftRadius: 20,
    borderTopRightRadius: 20,
  },
  bottomSheetTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    marginBottom: 10,
    color: '#333333',
  },
  bottomSheetImportance: {
    fontSize: 16,
    color: '#4782DA',
    fontWeight: 'bold',
    marginBottom: 15,
  },
  bottomSheetDescription: {
    fontSize: 16,
    marginBottom: 20,
    lineHeight: 24,
  },
  bottomSheetExplanation: {
    fontSize: 14,
    lineHeight: 22,
    backgroundColor: '#f0f7ff',
    padding: 15,
    borderRadius: 8,
    marginBottom: 20,
  },
  closeButton: {
    backgroundColor: '#4782DA',
    borderRadius: 8,
    paddingVertical: 12,
  },
});
