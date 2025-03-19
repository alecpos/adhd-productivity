import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, ScrollView, TextInput, ActivityIndicator } from 'react-native';
import { Card, Button, Slider, Divider } from '@rneui/themed';
import { Dimensions } from 'react-native';
import { BarChart } from 'react-native-chart-kit';

interface DurationEstimate {
  minEstimate: number;
  maxEstimate: number;
  confidence: number;
  mostLikely: number;
}

interface TaskComplexityFactor {
  id: string;
  name: string;
  score: number;
  description: string;
}

const mockTaskFactors: TaskComplexityFactor[] = [
  { id: '1', name: 'Cognitive Load', score: 7, description: 'Mental effort required' },
  { id: '2', name: 'Ambiguity', score: 5, description: 'How clear are the requirements' },
  { id: '3', name: 'Technical Complexity', score: 8, description: 'Technical difficulty' },
  { id: '4', name: 'Focus Required', score: 9, description: 'Level of attention needed' },
  { id: '5', name: 'Familiarity', score: 3, description: 'How familiar you are with this type of task' },
];

export const DurationEstimator = () => {
  const [taskDescription, setTaskDescription] = useState('');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [sliderValue, setSliderValue] = useState(60); // Minutes
  const [estimate, setEstimate] = useState<DurationEstimate | null>(null);
  const [showFactors, setShowFactors] = useState(false);
  const [taskFactors, setTaskFactors] = useState<TaskComplexityFactor[]>([]);
  
  const screenWidth = Dimensions.get('window').width - 40;
  
  // Format minutes to hours and minutes
  const formatMinutes = (minutes: number) => {
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    
    if (hours === 0) {
      return `${mins} min`;
    } else if (mins === 0) {
      return `${hours} hr`;
    } else {
      return `${hours} hr ${mins} min`;
    }
  };
  
  // Analyze task description
  const analyzeTask = () => {
    if (!taskDescription.trim()) return;
    
    setIsAnalyzing(true);
    setEstimate(null);
    setTaskFactors([]);
    
    // Simulate API call delay
    setTimeout(() => {
      // Mock estimate result
      const mockEstimate: DurationEstimate = {
        minEstimate: Math.max(30, Math.round(sliderValue * 0.7)),
        maxEstimate: Math.round(sliderValue * 1.5),
        confidence: 0.85,
        mostLikely: Math.round(sliderValue * 1.2),
      };
      
      setEstimate(mockEstimate);
      setTaskFactors(mockTaskFactors);
      setIsAnalyzing(false);
      setShowFactors(true);
    }, 1500);
  };
  
  // Get bar chart data for duration distribution
  const getChartData = () => {
    if (!estimate) return null;
    
    // Create a simplified distribution around the most likely estimate
    const step = Math.round((estimate.maxEstimate - estimate.minEstimate) / 5);
    const labels = [];
    const data = [];
    
    for (let i = 0; i < 5; i++) {
      const value = estimate.minEstimate + i * step;
      labels.push(formatMinutes(value));
      
      // Create a normal-like distribution with peak at the most likely value
      const distanceFromMostLikely = Math.abs(value - estimate.mostLikely);
      const normalizedDistance = distanceFromMostLikely / (estimate.maxEstimate - estimate.minEstimate);
      const height = Math.max(0.1, 1 - normalizedDistance * 1.5);
      data.push(Math.round(height * 100));
    }
    
    return {
      labels,
      datasets: [
        {
          data,
          color: (opacity = 1) => `rgba(71, 130, 218, ${opacity})`
        }
      ]
    };
  };
  
  const chartConfig = {
    backgroundGradientFrom: "#ffffff",
    backgroundGradientTo: "#ffffff",
    decimalPlaces: 0,
    color: (opacity = 1) => `rgba(71, 130, 218, ${opacity})`,
    labelColor: (opacity = 1) => `rgba(0, 0, 0, ${opacity})`,
    style: {
      borderRadius: 16,
    },
    barPercentage: 0.8,
  };
  
  return (
    <ScrollView style={styles.container}>
      <Card containerStyle={styles.card}>
        <Card.Title>Task Duration Estimator</Card.Title>
        <Text style={styles.description}>
          Our Bayesian prediction network analyzes task descriptions to provide more accurate time estimates.
        </Text>
        
        <Text style={styles.label}>Task Description</Text>
        <TextInput
          style={styles.input}
          value={taskDescription}
          onChangeText={setTaskDescription}
          placeholder="Describe your task in detail..."
          multiline
          numberOfLines={4}
        />
        
        <Text style={styles.label}>Your Estimate: {formatMinutes(sliderValue)}</Text>
        <View style={styles.sliderContainer}>
          <Text style={styles.sliderLabel}>15min</Text>
          <Slider
            value={sliderValue}
            onValueChange={setSliderValue}
            minimumValue={15}
            maximumValue={240}
            step={5}
            thumbStyle={styles.sliderThumb}
            thumbTintColor="#4782DA"
            minimumTrackTintColor="#4782DA"
            maximumTrackTintColor="#e0e0e0"
            style={styles.slider}
          />
          <Text style={styles.sliderLabel}>4hrs</Text>
        </View>
        
        <Button
          title="Analyze Task"
          onPress={analyzeTask}
          disabled={!taskDescription.trim() || isAnalyzing}
          loading={isAnalyzing}
          buttonStyle={styles.button}
        />
      </Card>
      
      {isAnalyzing && (
        <Card containerStyle={styles.card}>
          <ActivityIndicator size="large" color="#4782DA" />
          <Text style={styles.analyzingText}>Analyzing task complexity...</Text>
        </Card>
      )}
      
      {estimate && (
        <Card containerStyle={styles.card}>
          <Card.Title>Estimated Duration</Card.Title>
          
          <View style={styles.estimateContainer}>
            <View style={styles.estimateBox}>
              <Text style={styles.estimateLabel}>Minimum</Text>
              <Text style={styles.estimateValue}>{formatMinutes(estimate.minEstimate)}</Text>
            </View>
            <View style={styles.estimateBox}>
              <Text style={styles.estimateLabel}>Most Likely</Text>
              <Text style={[styles.estimateValue, styles.mostLikely]}>{formatMinutes(estimate.mostLikely)}</Text>
            </View>
            <View style={styles.estimateBox}>
              <Text style={styles.estimateLabel}>Maximum</Text>
              <Text style={styles.estimateValue}>{formatMinutes(estimate.maxEstimate)}</Text>
            </View>
          </View>
          
          <Text style={styles.confidenceText}>
            Confidence: {Math.round(estimate.confidence * 100)}%
          </Text>
          
          <Divider style={styles.divider} />
          
          <Text style={styles.chartTitle}>Duration Distribution</Text>
          <BarChart
            data={getChartData() || { labels: [], datasets: [{ data: [] }] }}
            width={screenWidth}
            height={220}
            chartConfig={chartConfig}
            style={styles.chart}
            showValuesOnTopOfBars
            withHorizontalLabels={false}
          />
          
          <Text style={styles.explanationText}>
            The most likely duration is {formatMinutes(estimate.mostLikely)}, which is {
              estimate.mostLikely > sliderValue 
                ? `${Math.round((estimate.mostLikely - sliderValue) / sliderValue * 100)}% longer` 
                : `${Math.round((sliderValue - estimate.mostLikely) / sliderValue * 100)}% shorter`
            } than your estimate.
          </Text>
          
          <Button
            title={showFactors ? "Hide Complexity Factors" : "Show Complexity Factors"}
            type="outline"
            onPress={() => setShowFactors(!showFactors)}
            buttonStyle={styles.secondaryButton}
          />
        </Card>
      )}
      
      {showFactors && taskFactors.length > 0 && (
        <Card containerStyle={styles.card}>
          <Card.Title>Task Complexity Analysis</Card.Title>
          
          {taskFactors.map((factor) => (
            <View key={factor.id} style={styles.factorContainer}>
              <View style={styles.factorHeader}>
                <Text style={styles.factorName}>{factor.name}</Text>
                <View style={styles.factorScoreContainer}>
                  <Text style={styles.factorScore}>{factor.score}/10</Text>
                </View>
              </View>
              <Text style={styles.factorDescription}>{factor.description}</Text>
              <View style={styles.factorBarContainer}>
                <View 
                  style={[
                    styles.factorBar, 
                    { width: `${factor.score * 10}%`, backgroundColor: getScoreColor(factor.score) }
                  ]} 
                />
              </View>
            </View>
          ))}
          
          <Text style={styles.factorExplanation}>
            These factors were identified by our NLP Complexity Analyzer from your task description
            and historical performance data. High scores indicate areas that may increase task duration.
          </Text>
        </Card>
      )}
    </ScrollView>
  );
};

const getScoreColor = (score: number) => {
  if (score <= 3) return '#47DA9B'; // Good (low complexity) - green
  if (score <= 6) return '#DAA147'; // Medium complexity - amber
  return '#DA4747'; // High complexity - red
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
  description: {
    fontSize: 14,
    marginBottom: 15,
    textAlign: 'center',
  },
  label: {
    fontSize: 16,
    fontWeight: 'bold',
    marginBottom: 8,
  },
  input: {
    borderWidth: 1,
    borderColor: '#e0e0e0',
    borderRadius: 8,
    padding: 10,
    fontSize: 16,
    minHeight: 100,
    textAlignVertical: 'top',
    marginBottom: 15,
  },
  sliderContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 20,
  },
  slider: {
    flex: 1,
    marginHorizontal: 10,
  },
  sliderLabel: {
    fontSize: 12,
    color: '#888888',
  },
  sliderThumb: {
    width: 20,
    height: 20,
    borderRadius: 10,
  },
  button: {
    borderRadius: 8,
    padding: 12,
    backgroundColor: '#4782DA',
  },
  analyzingText: {
    textAlign: 'center',
    marginTop: 15,
    fontSize: 16,
  },
  estimateContainer: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    marginVertical: 15,
  },
  estimateBox: {
    alignItems: 'center',
    padding: 10,
  },
  estimateLabel: {
    fontSize: 14,
    color: '#666666',
    marginBottom: 5,
  },
  estimateValue: {
    fontSize: 18,
    fontWeight: 'bold',
  },
  mostLikely: {
    color: '#4782DA',
    fontSize: 22,
  },
  confidenceText: {
    textAlign: 'center',
    fontSize: 16,
    marginBottom: 10,
  },
  divider: {
    marginVertical: 15,
  },
  chartTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    marginBottom: 10,
    textAlign: 'center',
  },
  chart: {
    marginVertical: 8,
    borderRadius: 16,
  },
  explanationText: {
    fontSize: 14,
    marginTop: 10,
    marginBottom: 15,
    textAlign: 'center',
  },
  secondaryButton: {
    borderRadius: 8,
    borderColor: '#4782DA',
  },
  factorContainer: {
    marginBottom: 15,
  },
  factorHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 5,
  },
  factorName: {
    fontSize: 16,
    fontWeight: 'bold',
  },
  factorScoreContainer: {
    backgroundColor: '#f0f0f0',
    paddingHorizontal: 10,
    paddingVertical: 2,
    borderRadius: 10,
  },
  factorScore: {
    fontSize: 14,
    fontWeight: 'bold',
  },
  factorDescription: {
    fontSize: 14,
    color: '#666666',
    marginBottom: 5,
  },
  factorBarContainer: {
    height: 8,
    backgroundColor: '#e0e0e0',
    borderRadius: 4,
    overflow: 'hidden',
  },
  factorBar: {
    height: '100%',
  },
  factorExplanation: {
    fontSize: 14,
    fontStyle: 'italic',
    marginTop: 10,
  },
}); 