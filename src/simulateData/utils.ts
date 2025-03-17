/**
 * Utility functions for data simulation
 */

/**
 * Generate a random number between min and max (inclusive)
 */
export function randomInRange(min: number, max: number): number {
  return Math.random() * (max - min) + min;
}

/**
 * Generate a random integer between min and max (inclusive)
 */
export function randomIntInRange(min: number, max: number): number {
  min = Math.ceil(min);
  max = Math.floor(max);
  return Math.floor(Math.random() * (max - min + 1)) + min;
}

/**
 * Generate a random date between start and end dates
 */
export function randomDate(start: Date, end: Date): Date {
  return new Date(start.getTime() + Math.random() * (end.getTime() - start.getTime()));
}

/**
 * Generate a random date string in ISO format within the past N months
 */
export function randomDateInPastMonths(months: number): string {
  const now = new Date();
  const pastDate = new Date();
  pastDate.setMonth(now.getMonth() - months);
  return randomDate(pastDate, now).toISOString().split('T')[0];
}

/**
 * Generate a random ID with a given prefix
 */
export function generateId(prefix: string, length: number = 6): string {
  const randomPart = Math.random().toString(36).substring(2, 2 + length);
  return `${prefix}-${randomPart}`;
}

/**
 * Pick a random element from an array
 */
export function randomPick<T>(array: T[]): T {
  return array[Math.floor(Math.random() * array.length)];
}

/**
 * Generate a random boolean with a given probability of being true
 */
export function randomBoolean(probability: number = 0.5): boolean {
  return Math.random() < probability;
}

/**
 * Generate a random value with a trend (for time series data)
 * @param baseValue The base value
 * @param trendFactor How much the trend affects the value (0-1)
 * @param noiseLevel How much random noise to add (0-1)
 * @param direction 1 for upward trend, -1 for downward trend
 */
export function valueWithTrend(
  baseValue: number,
  trendFactor: number,
  noiseLevel: number,
  direction: number = 1
): number {
  const trend = baseValue * trendFactor * direction;
  const noise = randomInRange(-baseValue * noiseLevel, baseValue * noiseLevel);
  return baseValue + trend + noise;
}

/**
 * Generate a series of values with a trend
 */
export function generateTrendSeries(
  startValue: number,
  count: number,
  trendFactor: number,
  noiseLevel: number,
  direction: number = 1
): number[] {
  const series: number[] = [];
  let currentValue = startValue;
  
  for (let i = 0; i < count; i++) {
    currentValue = valueWithTrend(currentValue, trendFactor, noiseLevel, direction);
    series.push(currentValue);
  }
  
  return series;
}

/**
 * Common medical conditions for random generation
 */
export const commonMedicalConditions = [
  'Hypertension',
  'Type 2 Diabetes',
  'Asthma',
  'Hypothyroidism',
  'Hyperlipidemia',
  'GERD',
  'Osteoarthritis',
  'Depression',
  'Anxiety',
  'Obesity',
  'Chronic Kidney Disease',
  'COPD',
  'Atrial Fibrillation',
  'Coronary Artery Disease',
  'Migraine',
  'Rheumatoid Arthritis',
  'Osteoporosis',
  'Anemia',
  'Sleep Apnea',
  'None'
];

/**
 * Format a number to a specific precision
 */
export function formatNumber(num: number, precision: number = 2): number {
  return Number(num.toFixed(precision));
}