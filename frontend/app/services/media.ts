import * as ImageManipulator from 'expo-image-manipulator';

interface ImageOptimizationOptions {
  maxWidth?: number;
  maxHeight?: number;
  quality?: number;
}

export const optimizeImage = async (
  uri: string,
  options: ImageOptimizationOptions = {}
) => {
    const {
      maxWidth = 800,
      maxHeight = 800,
      quality = 0.7
    } = options;

    try {
        const result = await ImageManipulator.manipulateAsync(
            uri,
            [{ resize: { width: maxWidth, height: maxHeight } }],
            { compress: quality }
        );
        return result.uri;
    } catch (error) {
        console.error('Error optimizing image:', error);
        return uri; // Return original URI if optimization fails
    }
};
