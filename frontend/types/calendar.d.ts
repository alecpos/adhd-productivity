declare module 'react-native-calendars' {
import { TextStyle } from 'react-native';

  import type { ViewStyle} from 'react-native';
  
  export interface DayProps {
    dateString: string;
    day: number;
    month: number;
    year: number;
    timestamp: number;
  }

  export type DateData = DayProps;

  interface Dot {
    color: string;
    selectedDotColor?: string;
  }

  export interface MarkedDates {
    [date: string]: {
      selected?: boolean;
      marked?: boolean;
      selectedColor?: string;
      dotColor?: string;
      disabled?: boolean;
      dots?: Dot[];
    };
  }

  export interface CalendarProps {
    current?: string;
    minDate?: string;
    maxDate?: string;
    onDayPress?: (day: DateData) => void;
    onDayLongPress?: (day: DateData) => void;
    monthFormat?: string;
    hideArrows?: boolean;
    hideExtraDays?: boolean;
    disableMonthChange?: boolean;
    firstDay?: number;
    hideDayNames?: boolean;
    showWeekNumbers?: boolean;
    onPressArrowLeft?: (subtractMonth: () => void) => void;
    onPressArrowRight?: (addMonth: () => void) => void;
    markedDates?: MarkedDates;
    markingType?: 'dot' | 'multi-dot' | 'period' | 'multi-period' | 'custom';
    style?: ViewStyle;
    theme?: {
      backgroundColor?: string;
      calendarBackground?: string;
      textSectionTitleColor?: string;
      selectedDayBackgroundColor?: string;
      selectedDayTextColor?: string;
      todayTextColor?: string;
      dayTextColor?: string;
      textDisabledColor?: string;
      dotColor?: string;
      selectedDotColor?: string;
      arrowColor?: string;
      monthTextColor?: string;
      textDayFontFamily?: string;
      textMonthFontFamily?: string;
      textDayHeaderFontFamily?: string;
      textDayFontWeight?: string;
      textMonthFontWeight?: string;
      textDayHeaderFontWeight?: string;
      textDayFontSize?: number;
      textMonthFontSize?: number;
      textDayHeaderFontSize?: number;
    };
  }

  export class Calendar extends React.Component<CalendarProps> {}
} 