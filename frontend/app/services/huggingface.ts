import { HfInference } from '@huggingface/inference';

interface EmotionResult {
  label: string;
  score: number;
}

interface EmotionClassification {
  label: string;
  score: number;
}

class HuggingFaceService {
  private hf: HfInference;

  constructor() {
    this.hf = new HfInference(process.env.EXPO_PUBLIC_HUGGINGFACE_API_KEY);
  }

  async analyzeSentiment(text: string): Promise<number> {
    try {
      const result = await this.hf.textClassification({
        model: 'SamLowe/roberta-base-go_emotions',
        inputs: text,
      });

      // Calculate sentiment score based on emotion labels
      const emotions = Array.isArray(result) ? result[0] : result;
      const sentimentScore = this.calculateSentimentScore(emotions);
      return sentimentScore;
    } catch (error) {
      console.error('Error analyzing sentiment:', error);
      throw error;
    }
  }

  async detectEmotions(text: string): Promise<EmotionResult> {
    try {
      const result = await this.hf.textClassification({
        model: 'SamLowe/roberta-base-go_emotions',
        inputs: text,
      });

      const emotions = Array.isArray(result) ? result[0] : result;
      return {
        label: emotions.label,
        score: emotions.score
      };
    } catch (error) {
      console.error('Error detecting emotions:', error);
      throw error;
    }
  }

  async generateRecommendations(prompt: string): Promise<string[]> {
    try {
      const result = await this.hf.textGeneration({
        model: 'tiiuae/falcon-7b-instruct',
        inputs: prompt,
        parameters: {
          max_new_tokens: 150,
          temperature: 0.7,
          top_p: 0.95,
          do_sample: true,
        }
      });

      const recommendations = this.parseRecommendations(result.generated_text);
      return recommendations;
    } catch (error) {
      console.error('Error generating recommendations:', error);
      throw error;
    }
  }

  async getTaskBreakdown(prompt: string): Promise<string[]> {
    try {
      const result = await this.hf.textGeneration({
        model: 'tiiuae/falcon-7b-instruct',
        inputs: `Break down this ADHD task into smaller, manageable steps:
        ${prompt}
        
        Format the response as a list of steps, with each step being specific and actionable.
        Consider executive function challenges and provide clear, concrete steps.`,
        parameters: {
          max_new_tokens: 200,
          temperature: 0.7,
          top_p: 0.95,
          do_sample: true,
        }
      });

      // Parse the generated text into an array of steps
      const steps = result.generated_text
        .split('\n')
        .map(line => line.trim())
        .filter(line => line.match(/^\d+\.|^\-/)) // Match numbered lists or bullet points
        .map(line => line.replace(/^\d+\.\s*|\-\s*/, '')); // Remove numbers/bullets

      return steps;
    } catch (error) {
      console.error('Error getting task breakdown:', error);
      throw error;
    }
  }

  private calculateSentimentScore(emotions: EmotionClassification | EmotionClassification[]): number {
    // If emotions is a single object, wrap it in an array
    const emotionsArray = Array.isArray(emotions) ? emotions : [emotions];
    
    const positiveEmotions = ['joy', 'love', 'optimism', 'relief'];
    const negativeEmotions = ['sadness', 'fear', 'anger', 'disgust'];

    return emotionsArray.reduce((score: number, emotion: EmotionClassification) => {
      if (positiveEmotions.includes(emotion.label.toLowerCase())) {
        return score + emotion.score;
      }
      if (negativeEmotions.includes(emotion.label.toLowerCase())) {
        return score - emotion.score;
      }
      return score;
    }, 0);
  }

  private parseRecommendations(text: string): string[] {
    return text
      .split('\n')
      .filter(line => line.trim().length > 0)
      .map(line => line.replace(/^\d+\.\s*/, '').trim())
      .slice(0, 3);
  }
}

export const huggingFaceService = new HuggingFaceService();
export default huggingFaceService; 