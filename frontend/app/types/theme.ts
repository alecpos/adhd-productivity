import type { Theme } from '@rneui/themed';

export interface CustomTheme extends Theme {
    fontSize: {
        xs: number;
        sm: number;
        md: number;
        lg: number;
        xl: number;
    };
} 