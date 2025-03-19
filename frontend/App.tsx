import React from 'react';
import { registerRootComponent } from 'expo';
import SimpleTestApp from './SimpleTestApp';

export default function App() {
  return <SimpleTestApp />;
}

// Register as the root component
registerRootComponent(App);
