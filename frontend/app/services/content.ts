import { createClient } from '@sanity/client';

export const sanityClient = createClient({
  projectId: process.env.EXPO_PUBLIC_SANITY_PROJECT_ID || '',
  dataset: process.env.EXPO_PUBLIC_SANITY_DATASET || 'production',
  useCdn: true,
  apiVersion: '2024-03-14',
});

// Type definitions for your content
export interface ContentTypes {
  mentalHealthTips: {
    title: string;
    content: string;
    category: string;
  }[];
  copingStrategies: {
    title: string;
    description: string;
    difficulty: number;
  }[];
}

export const getContent = async (query: string) => {
  try {
    return await sanityClient.fetch(query);
  } catch (error) {
    console.error('Error fetching content:', error);
    throw error;
  }
};
