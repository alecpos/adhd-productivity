import * as React from 'react';

import renderer from 'react-test-renderer';

// Mock the dependencies
jest.mock('@rneui/themed', () => ({
  Text: 'Text',
  makeStyles: () => () => ({
    monoText: {
      fontFamily: 'SpaceMono',
      color: '#000000'
    }
  }),
  useTheme: () => ({
    theme: {
      colors: {
        text: '#000000'
      }
    }
  })
}));

jest.mock('@rneui/base', () => ({
  TextProps: {}
}));

import { MonoText } from '../StyledText';

describe('MonoText', () => {
  it('renders correctly', () => {
    const tree = renderer.create(<MonoText>Snapshot test!</MonoText>).toJSON();
    expect(tree).toMatchSnapshot();
  });
});
