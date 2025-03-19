declare module 'expo-router' {
  import type { ComponentType } from 'react';

  import type { ViewProps } from 'react-native';

  export interface ScreenProps extends ViewProps {
    name: string;
    options?: any;
    component?: ComponentType<any>;
    href?: string | null;
  }

  export interface TabsProps extends ViewProps {
    screenOptions?: any;
    children?: React.ReactNode;
  }

  export interface StackProps extends ViewProps {
    screenOptions?: any;
    children?: React.ReactNode;
  }

  export const Stack: React.ComponentType<StackProps> & {
    Screen: React.ComponentType<ScreenProps>;
  };

  export const Tabs: React.ComponentType<TabsProps> & {
    Screen: React.ComponentType<ScreenProps>;
  };

  export function Slot(props: ViewProps): JSX.Element;
  export function useRouter(): {
    push: (route: string) => void;
    replace: (route: string) => void;
    back: () => void;
  };
  export function useSegments(): string[];
  export function Link(props: { href: string; [key: string]: any }): JSX.Element;
  export function Redirect(props: { href: string }): JSX.Element;

  export type StaticRoutes = string;
  export type RelativePathString = string;
} 