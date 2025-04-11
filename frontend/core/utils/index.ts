export const formatDate = (date: Date): string => {
    return new Intl.DateTimeFormat('en-US').format(date);
};

export const validateEmail = (email: string): boolean => {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
};

export const formatTime = (minutes: number): string => {
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    return `${hours}h ${mins}m`;
};

export const calculateEnergyScore = (levels: number[]): number => {
    if (!levels.length) return 0;
    return levels.reduce((sum, level) => sum + level, 0) / levels.length;
};

export const debounce = <T extends (...args: any[]) => any>(
    func: T,
    wait: number
): ((...args: Parameters<T>) => void) => {
    let timeout: NodeJS.Timeout;

    return (...args: Parameters<T>) => {
        clearTimeout(timeout);
        timeout = setTimeout(() => func(...args), wait);
    };
};
