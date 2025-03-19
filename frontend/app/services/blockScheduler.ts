import api from '@/lib/api';

export interface ScheduleBlocksRequest {
    start_date: string;
    end_date: string;
    focus_time?: number;
    break_time?: number;
    long_break_time?: number;
    blocks_before_long_break?: number;
    preferred_hours?: number[];
}

export interface ScheduleBlock {
    task_id: string;
    focus_event?: any;
    break_event?: any;
    start_time: string;
    end_time: string;
    type: 'focus' | 'break';
    is_long_break?: boolean;
}

export interface ScheduleBlocksResponse {
    scheduled_blocks: ScheduleBlock[];
    message: string;
}

export interface ScheduleStats {
    total_focus_time_minutes: number;
    total_focus_blocks: number;
    total_breaks: number;
    average_focus_time: number;
    completion_rate: number;
    most_productive_hour: number;
    focus_time_distribution: { [hour: string]: number };
    long_breaks_taken: number;
    focus_time_adjustments: {
        energy_based: number;
        mental_health_based: number;
    };
}

const blockSchedulerService = {
    async scheduleBlocks(request: ScheduleBlocksRequest): Promise<ScheduleBlocksResponse> {
        try {
            const response = await api.post('/block-scheduler/schedule', request);
            return response.data;
        } catch (error) {
            console.error('Error scheduling blocks:', error);
            throw error;
        }
    },

    async getScheduleStats(startDate: string, endDate: string): Promise<ScheduleStats> {
        try {
            const response = await api.get('/block-scheduler/stats', {
                params: {
                    start_date: startDate,
                    end_date: endDate,
                },
            });
            return response.data;
        } catch (error) {
            console.error('Error getting schedule stats:', error);
            throw error;
        }
    },

    // Helper function to format schedule blocks for calendar display
    formatBlocksForCalendar(blocks: ScheduleBlock[]) {
        return blocks.map(block => ({
            id: block.type === 'focus' ? block.focus_event?.id : block.break_event?.id,
            title: block.type === 'focus' 
                ? `Focus Session${block.focus_event?.title ? `: ${block.focus_event.title}` : ''}`
                : `${block.is_long_break ? 'Long Break' : 'Break'} Time`,
            start: new Date(block.start_time),
            end: new Date(block.end_time),
            type: block.type,
            isLongBreak: block.is_long_break,
            color: block.type === 'focus' ? '#4CAF50' : '#2196F3',
            textColor: '#FFFFFF',
        }));
    },

    // Helper function to get suggested schedule times
    getSuggestedScheduleTimes(preferredHours: number[] = [9, 10, 11, 12, 13, 14, 15, 16]) {
        const now = new Date();
        const tomorrow = new Date(now);
        tomorrow.setDate(tomorrow.getDate() + 1);
        
        // Reset to start of day
        tomorrow.setHours(0, 0, 0, 0);
        
        const suggestedTimes = [];
        for (const hour of preferredHours) {
            const time = new Date(tomorrow);
            time.setHours(hour);
            suggestedTimes.push(time);
        }
        
        return suggestedTimes;
    },

    // Helper function to check if a time slot is available
    async isTimeSlotAvailable(
        startTime: Date,
        duration: number,
        existingEvents: any[]
    ): Promise<boolean> {
        const endTime = new Date(startTime.getTime() + duration * 60000);
        
        return !existingEvents.some(event => {
            const eventStart = new Date(event.start);
            const eventEnd = new Date(event.end);
            return (startTime < eventEnd && endTime > eventStart);
        });
    }
};

export default blockSchedulerService; 