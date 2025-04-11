declare module 'react-native-chart-kit' {
  import type { ViewStyle } from 'react-native';

  interface ChartConfig {
    backgroundColor?: string;
    backgroundGradientFrom?: string;
    backgroundGradientTo?: string;
    decimalPlaces?: number;
    color?: (opacity: number) => string;
    labelColor?: (opacity: number) => string;
    style?: ViewStyle;
    propsForDots?: object;
    propsForLabels?: object;
  }

  interface LineChartData {
    labels: string[];
    datasets: {
      data: number[];
      color?: (opacity: number) => string;
      strokeWidth?: number;
    }[];
  }

  interface LineChartProps {
    data: LineChartData;
    width: number;
    height: number;
    chartConfig: ChartConfig;
    bezier?: boolean;
    style?: ViewStyle;
    withDots?: boolean;
    withShadow?: boolean;
    withInnerLines?: boolean;
    withOuterLines?: boolean;
    withHorizontalLabels?: boolean;
    withVerticalLabels?: boolean;
    yAxisLabel?: string;
    yAxisSuffix?: string;
    yAxisInterval?: number;
    onDataPointClick?: (data: { value: number; dataset: any; getColor: any }) => void;
  }

  export class LineChart extends React.Component<LineChartProps> {}
}
