// This is a mock version of expo-file-system for web compatibility

// Standard directory and file URIs
export const documentDirectory = 'file:///document/';
export const cacheDirectory = 'file:///cache/';
export const bundleDirectory = 'file:///bundle/';
export const downloadDirectory = 'file:///downloads/';

// Mock file info interface
export interface FileInfo {
  exists: boolean;
  isDirectory: boolean;
  modificationTime: number;
  size: number;
  uri: string;
}

// Mock file system
class FileSystem {
  // Reading files
  async readAsStringAsync(fileUri: string): Promise<string> {
    console.warn('FileSystem.readAsStringAsync is mocked for web', fileUri);
    return 'mock file content';
  }

  async readAsDataURLAsync(fileUri: string): Promise<string> {
    console.warn('FileSystem.readAsDataURLAsync is mocked for web', fileUri);
    return 'data:text/plain;base64,bW9jayBkYXRh';
  }

  async getInfoAsync(fileUri: string): Promise<FileInfo> {
    console.warn('FileSystem.getInfoAsync is mocked for web', fileUri);
    return {
      exists: true,
      isDirectory: false,
      modificationTime: Date.now(),
      size: 0,
      uri: fileUri,
    };
  }

  // Writing files
  async writeAsStringAsync(fileUri: string, contents: string): Promise<void> {
    console.warn('FileSystem.writeAsStringAsync is mocked for web', { fileUri, contents });
  }

  async deleteAsync(fileUri: string): Promise<void> {
    console.warn('FileSystem.deleteAsync is mocked for web', fileUri);
  }

  async moveAsync(options: { from: string; to: string }): Promise<void> {
    console.warn('FileSystem.moveAsync is mocked for web', options);
  }

  async copyAsync(options: { from: string; to: string }): Promise<void> {
    console.warn('FileSystem.copyAsync is mocked for web', options);
  }

  async makeDirectoryAsync(dirUri: string): Promise<void> {
    console.warn('FileSystem.makeDirectoryAsync is mocked for web', dirUri);
  }

  async downloadAsync(uri: string, fileUri: string): Promise<{ status: number; uri: string }> {
    console.warn('FileSystem.downloadAsync is mocked for web', { uri, fileUri });
    return { status: 200, uri: fileUri };
  }
}

// Create singleton instance
const fileSystem = new FileSystem();

// Export default and static methods
export default {
  ...fileSystem,
  documentDirectory,
  cacheDirectory,
  bundleDirectory,
  downloadDirectory,
}; 