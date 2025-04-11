declare module '@huggingface/inference' {
  interface TextClassificationParameters {
    max_length?: number;
    padding?: boolean | 'longest' | 'max_length' | 'do_not_pad';
    truncation?: boolean;
    wait_for_model?: boolean;
  }

  interface TextGenerationParameters {
    max_new_tokens?: number;
    temperature?: number;
    top_p?: number;
    do_sample?: boolean;
    wait_for_model?: boolean;
  }

  export class HfInference {
    constructor(accessToken?: string);
    textClassification(options: {
      model: string;
      inputs: string;
      parameters?: TextClassificationParameters;
    }): Promise<{
      label: string;
      score: number;
    }>;
    textGeneration(options: {
      model: string;
      inputs: string;
      parameters?: TextGenerationParameters;
    }): Promise<{
      generated_text: string;
    }>;
  }
}
