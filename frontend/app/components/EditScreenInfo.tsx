import { Text } from '@rneui/themed';
import { Button } from '@rneui/themed';
import { StyleSheet, View } from 'react-native';

export default function EditScreenInfo({ path }: { path: string }) {
  return (
    <View style={styles.container}>
      <View style={styles.getStartedContainer}>
        <Text style={styles.getStartedText}>
          This screen is located at:
        </Text>
        <Text style={styles.pathText}>
          {path}
        </Text>
      </View>

      <View style={styles.helpContainer}>
        <Button
          title="Help"
          type="outline"
          onPress={() => {
            // Add help functionality here
          }}
        />
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    alignItems: 'center',
    marginHorizontal: 50,
  },
  getStartedContainer: {
    alignItems: 'center',
    marginHorizontal: 50,
    marginBottom: 20,
  },
  getStartedText: {
    fontSize: 17,
    lineHeight: 24,
    textAlign: 'center',
    marginBottom: 8,
  },
  pathText: {
    fontSize: 15,
    lineHeight: 22,
    textAlign: 'center',
    fontFamily: 'SpaceMono',
  },
  helpContainer: {
    marginTop: 15,
    marginHorizontal: 20,
    alignItems: 'center',
  },
});
