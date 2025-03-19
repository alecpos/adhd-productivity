import React from 'react';

import { Text, makeStyles, useTheme } from '@rneui/themed';
import { StyleSheet, View } from 'react-native';

import { ExternalLink } from './ExternalLink';
import { MonoText } from './StyledText';

export default function EditScreenInfo({ path }: { path: string }) {
  const { theme } = useTheme();
  const styles = useStyles();

  return (
    <View>
      <View style={styles.getStartedContainer}>
        <Text style={styles.getStartedText}>
          Open up the code for this screen:
        </Text>

        <View style={[styles.codeHighlightContainer, styles.homeScreenFilename]}>
          <MonoText>{path}</MonoText>
        </View>

        <Text style={styles.getStartedText}>
          Change any of the text, save the file, and your app will automatically update.
        </Text>
      </View>

      <View style={styles.helpContainer}>
        <ExternalLink
          style={styles.helpLink}
          href="https://docs.expo.io/get-started/create-a-new-app/#opening-the-app-on-your-phonetablet">
          <Text style={styles.helpLinkText}>
            Tap here if your app doesn't automatically update after making changes
          </Text>
        </ExternalLink>
      </View>
    </View>
  );
}

const useStyles = makeStyles((theme) => ({
  getStartedContainer: {
    alignItems: 'center',
    marginHorizontal: 50,
  },
  homeScreenFilename: {
    marginVertical: 7,
  },
  codeHighlightContainer: {
    borderRadius: 3,
    paddingHorizontal: 4,
    backgroundColor: theme.mode === 'dark' 
      ? 'rgba(255,255,255,0.05)' 
      : 'rgba(0,0,0,0.05)',
  },
  getStartedText: {
    fontSize: 17,
    lineHeight: 24,
    textAlign: 'center',
    color: theme.mode === 'dark' 
      ? 'rgba(255,255,255,0.8)' 
      : 'rgba(0,0,0,0.8)',
  },
  helpContainer: {
    marginTop: 15,
    marginHorizontal: 20,
    alignItems: 'center',
  },
  helpLink: {
    paddingVertical: 15,
  },
  helpLinkText: {
    textAlign: 'center',
    color: theme.colors.primary,
  },
}));
