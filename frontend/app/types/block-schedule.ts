export interface BlockSchedule {
    id: string;
    name: string;
    startTime: string;
    endTime: string;
    duration: number;
    description?: string;
    userId: string;
    createdAt: string;
    updatedAt: string;
}

export interface TimeBlock {
    startTime: Date;
    endTime: Date;
    type: 'focus' | 'break' | 'long-break';
    task?: string;
    priority?: number;
}

export interface SchedulingDecision {
    option: string;
    reasoning: string;
    timeBlocks: TimeBlock[];
    nextSteps?: string[];
}

export interface SchedulingSuggestion {
    availableBlocks: TimeBlock[];
    decisionTree: SchedulingDecision[];
    confidence: number;
}
