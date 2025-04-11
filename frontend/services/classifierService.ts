import AsyncStorage from '@react-native-async-storage/async-storage';

interface Pattern {
  pattern: string;
  category: string;
  rules: string[];
  examples: string[];
}

interface ClassificationResult {
  category: string;
  confidence: number;
  rules: string[];
}

interface KeywordCategories {
  task: {
    actions: string[];
    subjects: string[];
    timeframes: string[];
    priority: string[];
  };
  calendar: {
    actions: string[];
    subjects: string[];
    timeframes: string[];
    recurrence: string[];
  };
  mental_health: {
    emotions: string[];
    states: string[];
    intensity: string[];
    triggers: string[];
  };
  focus: {
    actions: string[];
    duration: string[];
    distractions: string[];
    goals: string[];
  };
}

type CategoryScores = {
  [K in keyof KeywordCategories]: number;
};

const STORAGE_KEY = 'learned_patterns';

class ClassifierService {
  private patterns: Pattern[] = [];
  private initialized = false;
  private categories: Set<string> = new Set([
    'task',
    'calendar',
    'mental_health',
    'focus',
    'unknown'
  ]);

  // Enhanced keyword mappings with context
  private readonly contextualKeywords: KeywordCategories = {
    task: {
      actions: ['do', 'complete', 'finish', 'submit', 'work on', 'handle', 'process', 'start', 'begin', 'initiate'],
      subjects: ['task', 'todo', 'assignment', 'project', 'report', 'deadline', 'work', 'responsibility', 'objective', 'goal'],
      timeframes: ['by', 'before', 'until', 'due', 'deadline', 'tomorrow', 'next week', 'tonight', 'this afternoon'],
      priority: ['urgent', 'important', 'critical', 'asap', 'priority', 'crucial', 'essential', 'vital', 'pressing']
    },
    calendar: {
      actions: ['meet', 'attend', 'schedule', 'plan', 'join', 'host', 'organize', 'book', 'reserve', 'arrange'],
      subjects: ['meeting', 'appointment', 'event', 'call', 'session', 'conference', 'workshop', 'seminar', 'presentation'],
      timeframes: ['at', 'on', 'from', 'until', 'between', 'during', 'this week', 'next month', 'tomorrow'],
      recurrence: ['daily', 'weekly', 'monthly', 'every', 'recurring', 'repeat', 'regular', 'routine', 'periodic']
    },
    mental_health: {
      emotions: ['happy', 'sad', 'anxious', 'stressed', 'overwhelmed', 'excited', 'worried', 'calm', 'frustrated', 'content', 'depressed', 'angry'],
      states: ['mood', 'feeling', 'emotion', 'mental', 'mindset', 'energy', 'motivation', 'attitude', 'spirit', 'wellbeing'],
      intensity: ['very', 'extremely', 'somewhat', 'slightly', 'really', 'incredibly', 'moderately', 'mildly', 'intensely'],
      triggers: ['because', 'due to', 'when', 'about', 'regarding', 'caused by', 'triggered by', 'related to', 'stems from']
    },
    focus: {
      actions: ['focus', 'concentrate', 'work', 'study', 'learn', 'read', 'write', 'practice', 'review', 'analyze'],
      duration: ['for', 'minutes', 'hours', 'pomodoro', 'session', 'period', 'block', 'interval', 'stretch'],
      distractions: ['distraction', 'interruption', 'noise', 'notification', 'alert', 'message', 'social media', 'email', 'phone'],
      goals: ['complete', 'achieve', 'finish', 'master', 'understand', 'learn', 'grasp', 'comprehend', 'accomplish']
    }
  };

  constructor() {
    this.loadPatterns();
  }

  private async loadPatterns() {
    try {
      // Check if we're in a browser environment
      if (typeof window !== 'undefined') {
        const storedPatterns = await AsyncStorage.getItem(STORAGE_KEY);
        if (storedPatterns) {
          this.patterns = JSON.parse(storedPatterns);
        }
      }
      this.initialized = true;
    } catch (error) {
      console.error('Error loading patterns:', error);
      this.initialized = true;
    }
  }

  private async savePatterns() {
    try {
      // Check if we're in a browser environment
      if (typeof window !== 'undefined') {
        await AsyncStorage.setItem(STORAGE_KEY, JSON.stringify(this.patterns));
      }
    } catch (error) {
      console.error('Error saving patterns:', error);
    }
  }

  // Add a new pattern to learn from
  async addPattern(pattern: Pattern): Promise<void> {
    // Wait for initialization if needed
    if (!this.initialized) {
      await new Promise<void>(resolve => {
        const checkInit = () => {
          if (this.initialized) resolve();
          else setTimeout(checkInit, 100);
        };
        checkInit();
      });
    }

    this.patterns.push(pattern);
    this.categories.add(pattern.category);
    await this.savePatterns();
  }

  // Get all learned patterns
  async getPatterns(): Promise<Pattern[]> {
    // Wait for initialization if needed
    if (!this.initialized) {
      await new Promise<void>(resolve => {
        const checkInit = () => {
          if (this.initialized) resolve();
          else setTimeout(checkInit, 100);
        };
        checkInit();
      });
    }

    return [...this.patterns];
  }

  // Get all known categories
  getCategories(): string[] {
    return [...this.categories];
  }

  // Classify input text
  classifyInput(input: string): ClassificationResult {
    const words = input.toLowerCase().split(' ');
    let maxConfidence = 0;
    let bestCategory = 'unknown';
    let matchedRules: string[] = [];

    // Extract context and sentiment
    const contexts = this.analyzeContext(input);
    const sentiment = this.analyzeSentiment(input);

    // Check semantic similarity with existing patterns
    this.patterns.forEach(pattern => {
      let confidence = this.calculateSemanticSimilarity(input, pattern.pattern);

      // Boost confidence based on context matches
      if (contexts.length > 0) {
        const patternContexts = this.analyzeContext(pattern.pattern);
        const contextMatchCount = contexts.filter(ctx => patternContexts.includes(ctx)).length;
        confidence += (contextMatchCount * 0.1);
      }

      // Adjust confidence based on sentiment match
      const patternSentiment = this.analyzeSentiment(pattern.pattern);
      if (sentiment.sentiment === patternSentiment.sentiment) {
        confidence += 0.1;
      }

      if (confidence > maxConfidence) {
        maxConfidence = confidence;
        bestCategory = pattern.category;
        matchedRules = pattern.rules;
      }
    });

    // Fallback to enhanced keyword-based classification
    if (maxConfidence < 0.3) {
      const keywordResult = this.classifyByKeywords(words);
      if (keywordResult.category !== 'unknown') {
        return {
          ...keywordResult,
          confidence: keywordResult.confidence + (contexts.length * 0.05) +
                     (sentiment.sentiment !== 'neutral' ? sentiment.intensity * 0.1 : 0)
        };
      }
    }

    return {
      category: bestCategory,
      confidence: maxConfidence,
      rules: matchedRules,
    };
  }

  // Basic keyword-based classification
  private classifyByKeywords(words: string[]): ClassificationResult {
    const scores: CategoryScores = {
      task: 0,
      calendar: 0,
      mental_health: 0,
      focus: 0
    };

    // Helper to check for phrase matches
    const containsPhrase = (text: string, phrase: string) =>
      text.toLowerCase().includes(phrase.toLowerCase());

    // Join words to check for multi-word phrases
    const text = words.join(' ').toLowerCase();

    // Calculate scores for each category
    (Object.entries(this.contextualKeywords) as [keyof CategoryScores, typeof this.contextualKeywords[keyof KeywordCategories]][]).forEach(([category, keywords]) => {
      Object.entries(keywords).forEach(([type, terms]) => {
        terms.forEach((term: string) => {
          if (containsPhrase(text, term)) {
            // Weight different types of matches
            switch (type) {
              case 'actions':
                scores[category] += 1.5;
                break;
              case 'subjects':
                scores[category] += 2;
                break;
              case 'timeframes':
              case 'duration':
                scores[category] += 1;
                break;
              case 'emotions':
              case 'intensity':
                scores[category] += 1.75;
                break;
              default:
                scores[category] += 1;
            }
          }
        });
      });
    });

    // Find highest scoring category
    let maxScore = 0;
    let bestCategory: keyof CategoryScores | 'unknown' = 'unknown';
    const matchedTerms: string[] = [];

    (Object.entries(scores) as [keyof CategoryScores, number][]).forEach(([category, score]) => {
      if (score > maxScore) {
        maxScore = score;
        bestCategory = category;

        // Collect matched terms for the winning category
        Object.values(this.contextualKeywords[category]).flat().forEach((term: string) => {
          if (containsPhrase(text, term)) {
            matchedTerms.push(term);
          }
        });
      }
    });

    // Calculate confidence based on score and text length
    const confidence = maxScore > 0
      ? Math.min(maxScore / (words.length * 0.75), 1)
      : 0;

    return {
      category: bestCategory,
      confidence,
      rules: matchedTerms
    };
  }

  // Enhanced rule extraction with NLP patterns
  extractRules(input: string): string[] {
    const rules: string[] = [];
    const text = input.toLowerCase();
    const sentences = text.split(/[.!?]+/).filter(Boolean);

    // Time expressions
    const timePatterns = [
      // Absolute time
      /\b(at|from|until)\s+(\d{1,2}(?::\d{2})?(?:\s*[ap]m)?)\b/i,
      // Relative time
      /\b(in|after|within)\s+(\d+)\s*(minutes?|hours?|days?|weeks?)\b/i,
      // Time of day
      /\b(morning|afternoon|evening|night|midnight|noon)\b/i,
      // Days
      /\b(today|tomorrow|yesterday|next|this)\s+(monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b/i,
      // Dates
      /\b(\d{1,2}(?:st|nd|rd|th)?)\s+(jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:tember)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)\b/i
    ];

    timePatterns.forEach(pattern => {
      const matches = text.match(new RegExp(pattern, 'gi'));
      if (matches) rules.push(...matches);
    });

    // Duration expressions
    const durationPatterns = [
      /\b(?:for|during)\s+(?:\d+\s+)?(?:minutes?|hours?|days?|weeks?)\b/gi,
      /\b(\d+)-(?:minute|hour|day|week)\b/gi,
      /\b(?:brief|short|long|extended)\s+(?:period|time|duration)\b/gi
    ];

    durationPatterns.forEach(pattern => {
      const matches = text.match(pattern);
      if (matches) rules.push(...matches);
    });

    // Conditional expressions
    const conditionalPatterns = [
      // Basic conditions
      /\b(?:if|when|unless|after|before|while)\b[^.!?]+/gi,
      // Complex conditions
      /\b(?:assuming|provided|given|in case|as long as)\b[^.!?]+/gi,
      // State conditions
      /\b(?:during|while|throughout|in)\s+(?:the|a|an)\s+\w+(?:\s+\w+){0,2}\b/gi
    ];

    conditionalPatterns.forEach(pattern => {
      const matches = text.match(pattern);
      if (matches) rules.push(...matches);
    });

    // Action patterns with context
    sentences.forEach(sentence => {
      const words = sentence.trim().split(/\s+/);
      if (words.length >= 3) {
        // Modal verbs and intentions
        const modalPattern = /\b(need|want|must|should|will|going|plan|intend|aim|hope)\s+to\b/i;
        if (modalPattern.test(sentence)) {
          rules.push(sentence.trim());
        }

        // Imperative mood
        const firstWord = words[0].toLowerCase();
        if (['create', 'make', 'set', 'start', 'begin', 'ensure', 'check', 'review'].includes(firstWord)) {
          rules.push(sentence.trim());
        }

        // Action phrases
        const actionPhrases = [
          /\b(?:work on|focus on|concentrate on|pay attention to)\b/i,
          /\b(?:take care of|handle|manage|deal with)\b/i,
          /\b(?:get done|complete|finish|accomplish)\b/i
        ];

        actionPhrases.forEach(phrase => {
          if (phrase.test(sentence)) {
            rules.push(sentence.trim());
          }
        });
      }
    });

    // Priority and importance markers
    const priorityPatterns = [
      /\b(?:high|medium|low)\s+priority\b/i,
      /\b(?:urgent|important|critical|essential|crucial)\b/i,
      /\b(?:asap|as soon as possible|right away|immediately)\b/i,
      /\b(?:can wait|not urgent|when possible)\b/i
    ];

    priorityPatterns.forEach(pattern => {
      const matches = text.match(pattern);
      if (matches) rules.push(...matches);
    });

    // Emotional and mental state expressions
    const statePatterns = [
      /\b(?:feel(?:ing)?|am|getting)\s+(?:very|really|quite|somewhat|a bit|slightly)?\s+(?:happy|sad|anxious|stressed|overwhelmed|excited|worried|calm)\b/i,
      /\b(?:my|the)\s+(?:mood|energy|focus|concentration|motivation)\s+(?:is|feels?|seems?)\b/i,
      /\b(?:having|experiencing|dealing with)\s+(?:trouble|difficulty|problems?|issues?)\s+(?:with|in|during)\b/i
    ];

    statePatterns.forEach(pattern => {
      const matches = text.match(pattern);
      if (matches) rules.push(...matches);
    });

    // Remove duplicates and normalize
    return [...new Set(rules.map(rule => rule.trim()))];
  }

  // Add semantic similarity checking
  private calculateSemanticSimilarity(text1: string, text2: string): number {
    const words1 = new Set(text1.toLowerCase().split(/\s+/));
    const words2 = new Set(text2.toLowerCase().split(/\s+/));

    const intersection = new Set([...words1].filter(word => words2.has(word)));
    const union = new Set([...words1, ...words2]);

    return intersection.size / union.size;
  }

  // Learn from user feedback
  async learnFromFeedback(input: string, correctCategory: string): Promise<void> {
    const rules = this.extractRules(input);
    const newPattern: Pattern = {
      pattern: input,
      category: correctCategory,
      rules,
      examples: [input],
    };
    await this.addPattern(newPattern);
  }

  // Clear all learned patterns
  async clearPatterns(): Promise<void> {
    this.patterns = [];
    await AsyncStorage.removeItem(STORAGE_KEY);
  }

  // Export patterns
  async exportPatterns(): Promise<string> {
    return JSON.stringify(this.patterns, null, 2);
  }

  // Import patterns
  async importPatterns(patternsJson: string): Promise<void> {
    try {
      const newPatterns = JSON.parse(patternsJson) as Pattern[];
      if (Array.isArray(newPatterns)) {
        this.patterns = newPatterns;
        await this.savePatterns();
      }
    } catch (error) {
      console.error('Error importing patterns:', error);
      throw new Error('Invalid patterns format');
    }
  }

  // Add sentiment analysis
  private analyzeSentiment(text: string): { sentiment: 'positive' | 'negative' | 'neutral', intensity: number } {
    const positiveWords = new Set([
      'good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic', 'happy', 'excited', 'productive', 'successful',
      'accomplished', 'confident', 'motivated', 'energetic', 'focused', 'efficient', 'effective', 'proud'
    ]);

    const negativeWords = new Set([
      'bad', 'terrible', 'awful', 'horrible', 'stressed', 'anxious', 'worried', 'overwhelmed', 'frustrated', 'tired',
      'exhausted', 'confused', 'difficult', 'challenging', 'hard', 'struggling', 'procrastinating', 'distracted'
    ]);

    const words = text.toLowerCase().split(/\s+/);
    let positiveCount = 0;
    let negativeCount = 0;

    words.forEach(word => {
      if (positiveWords.has(word)) positiveCount++;
      if (negativeWords.has(word)) negativeCount++;
    });

    const total = positiveCount + negativeCount;
    if (total === 0) return { sentiment: 'neutral', intensity: 0 };

    const sentiment = positiveCount > negativeCount ? 'positive' :
                     negativeCount > positiveCount ? 'negative' : 'neutral';
    const intensity = Math.abs(positiveCount - negativeCount) / words.length;

    return { sentiment, intensity };
  }

  // Add context awareness
  private analyzeContext(text: string): string[] {
    const contexts: string[] = [];

    // Time context
    if (text.match(/\b(morning|afternoon|evening|night|today|tomorrow|weekend)\b/i)) {
      contexts.push('time_specific');
    }

    // Location context
    if (text.match(/\b(at|in|from|to)\s+\w+(?:\s+\w+){0,2}\b/i)) {
      contexts.push('location_specific');
    }

    // People context
    if (text.match(/\b(with|and|team|group|colleague|friend|family)\b/i)) {
      contexts.push('people_involved');
    }

    // Energy level context
    if (text.match(/\b(tired|energetic|exhausted|fresh|sleepy|alert)\b/i)) {
      contexts.push('energy_related');
    }

    return contexts;
  }
}

export const classifierService = new ClassifierService();
