/**
 * A/B Testing Framework
 *
 * Comprehensive A/B testing system for optimizing journal UX:
 * - Variant management (create, deploy, track)
 * - User assignment (consistent hashing)
 * - Conversion tracking
 * - Statistical analysis
 * - Real-time results
 * - Multi-variant testing (A/B/C/D)
 */

export interface ABTest {
  id: string;
  name: string;
  description: string;
  status: 'draft' | 'active' | 'paused' | 'completed';
  variants: Variant[];
  targetAudience: TargetAudience;
  metrics: Metric[];
  startDate: Date;
  endDate?: Date;
  sampleSize?: number;
  confidenceLevel: number; // 0.9, 0.95, 0.99
  createdBy: string;
  results?: TestResults;
}

export interface Variant {
  id: string;
  name: string;
  description: string;
  trafficPercentage: number; // 0-100
  isControl: boolean;
  config: Record<string, any>; // Variant-specific configuration
  exposures: number;
  conversions: number;
  conversionRate: number;
}

export interface TargetAudience {
  userType?: 'all' | 'authors' | 'reviewers' | 'readers' | 'editors';
  location?: string[];
  deviceType?: 'desktop' | 'mobile' | 'tablet' | 'all';
  newUsers?: boolean;
  returningUsers?: boolean;
}

export interface Metric {
  id: string;
  name: string;
  type: 'conversion' | 'engagement' | 'revenue' | 'time';
  goal: 'increase' | 'decrease';
  baseline?: number;
  target?: number;
}

export interface TestResults {
  winner?: string; // Variant ID
  confidence: number; // 0-1
  improvement: number; // Percentage improvement over control
  statisticalSignificance: boolean;
  variantResults: VariantResult[];
  recommendations: string[];
}

export interface VariantResult {
  variantId: string;
  variantName: string;
  exposures: number;
  conversions: number;
  conversionRate: number;
  improvement: number; // vs control
  pValue: number;
  confidenceInterval: [number, number];
}

export interface UserAssignment {
  userId: string;
  testId: string;
  variantId: string;
  assignedAt: Date;
  exposedAt?: Date;
  convertedAt?: Date;
}

class ABTestingService {
  private activeTests: Map<string, ABTest> = new Map();
  private userAssignments: Map<string, Map<string, UserAssignment>> = new Map();

  /**
   * Initialize A/B testing service
   */
  async initialize(): Promise<void> {
    // Load active tests from backend
    const response = await fetch('/api/v1/ab-testing/active');
    const tests = await response.json();

    tests.forEach((test: ABTest) => {
      this.activeTests.set(test.id, test);
    });

    // Load user assignments from localStorage
    const storedAssignments = localStorage.getItem('ab_test_assignments');
    if (storedAssignments) {
      const assignments = JSON.parse(storedAssignments);
      Object.entries(assignments).forEach(([testId, variantId]) => {
        this.assignUserToVariant(this.getUserId(), testId, variantId as string);
      });
    }
  }

  /**
   * Get variant for user in a test
   */
  getVariant(testId: string, userId?: string): Variant | null {
    const user = userId || this.getUserId();
    const test = this.activeTests.get(testId);

    if (!test || test.status !== 'active') {
      return null;
    }

    // Check if user is already assigned
    const assignment = this.getUserAssignment(user, testId);
    if (assignment) {
      const variant = test.variants.find((v) => v.id === assignment.variantId);
      if (variant) {
        this.trackExposure(testId, assignment.variantId, user);
        return variant;
      }
    }

    // Check if user matches target audience
    if (!this.matchesTargetAudience(test.targetAudience)) {
      return test.variants.find((v) => v.isControl) || null;
    }

    // Assign user to variant
    const variant = this.assignToVariant(test, user);
    this.trackExposure(testId, variant.id, user);

    return variant;
  }

  /**
   * Check if variant is active for test
   */
  isVariantActive(testId: string, variantId: string): boolean {
    const assignment = this.getUserAssignment(this.getUserId(), testId);
    return assignment?.variantId === variantId;
  }

  /**
   * Get variant configuration
   */
  getVariantConfig<T = any>(testId: string, key: string, defaultValue: T): T {
    const variant = this.getVariant(testId);
    if (!variant || !variant.config) {
      return defaultValue;
    }
    return variant.config[key] !== undefined ? variant.config[key] : defaultValue;
  }

  /**
   * Track conversion event
   */
  async trackConversion(
    testId: string,
    metricId: string,
    value?: number
  ): Promise<void> {
    const userId = this.getUserId();
    const assignment = this.getUserAssignment(userId, testId);

    if (!assignment || assignment.convertedAt) {
      return; // Already converted or not in test
    }

    // Update assignment
    assignment.convertedAt = new Date();
    this.saveUserAssignments();

    // Send to backend
    await fetch('/api/v1/ab-testing/conversion', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        testId,
        variantId: assignment.variantId,
        metricId,
        userId,
        value,
        timestamp: new Date().toISOString(),
      }),
    });

    // Update local test data
    const test = this.activeTests.get(testId);
    if (test) {
      const variant = test.variants.find((v) => v.id === assignment.variantId);
      if (variant) {
        variant.conversions++;
        variant.conversionRate = variant.conversions / variant.exposures;
      }
    }
  }

  /**
   * Track custom event
   */
  async trackEvent(
    testId: string,
    eventName: string,
    properties?: Record<string, any>
  ): Promise<void> {
    const userId = this.getUserId();
    const assignment = this.getUserAssignment(userId, testId);

    if (!assignment) {
      return;
    }

    await fetch('/api/v1/ab-testing/event', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        testId,
        variantId: assignment.variantId,
        eventName,
        properties,
        userId,
        timestamp: new Date().toISOString(),
      }),
    });
  }

  /**
   * Get test results
   */
  async getTestResults(testId: string): Promise<TestResults | null> {
    try {
      const response = await fetch(`/api/v1/ab-testing/${testId}/results`);
      const results = await response.json();
      return results;
    } catch (error) {
      console.error('Failed to fetch test results:', error);
      return null;
    }
  }

  /**
   * Calculate statistical significance
   */
  calculateSignificance(
    controlConversions: number,
    controlExposures: number,
    variantConversions: number,
    variantExposures: number
  ): { pValue: number; significant: boolean } {
    // Simple z-test for proportions
    const p1 = controlConversions / controlExposures;
    const p2 = variantConversions / variantExposures;

    const pooledProportion =
      (controlConversions + variantConversions) /
      (controlExposures + variantExposures);

    const se = Math.sqrt(
      pooledProportion *
        (1 - pooledProportion) *
        (1 / controlExposures + 1 / variantExposures)
    );

    const zScore = (p2 - p1) / se;
    const pValue = 2 * (1 - this.normalCDF(Math.abs(zScore)));

    return {
      pValue,
      significant: pValue < 0.05,
    };
  }

  /**
   * Create new A/B test
   */
  async createTest(test: Omit<ABTest, 'id'>): Promise<ABTest> {
    const response = await fetch('/api/v1/ab-testing/tests', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(test),
    });

    const createdTest = await response.json();
    return createdTest;
  }

  /**
   * Start test
   */
  async startTest(testId: string): Promise<void> {
    await fetch(`/api/v1/ab-testing/tests/${testId}/start`, {
      method: 'POST',
    });

    const test = this.activeTests.get(testId);
    if (test) {
      test.status = 'active';
    }
  }

  /**
   * Stop test
   */
  async stopTest(testId: string): Promise<void> {
    await fetch(`/api/v1/ab-testing/tests/${testId}/stop`, {
      method: 'POST',
    });

    const test = this.activeTests.get(testId);
    if (test) {
      test.status = 'completed';
    }
  }

  // ==================== Private Methods ====================

  private assignToVariant(test: ABTest, userId: string): Variant {
    // Use consistent hashing for stable assignment
    const hash = this.hashString(userId + test.id);
    const bucket = hash % 100;

    let cumulative = 0;
    for (const variant of test.variants) {
      cumulative += variant.trafficPercentage;
      if (bucket < cumulative) {
        this.assignUserToVariant(userId, test.id, variant.id);
        return variant;
      }
    }

    // Fallback to control
    const control = test.variants.find((v) => v.isControl);
    if (control) {
      this.assignUserToVariant(userId, test.id, control.id);
      return control;
    }

    return test.variants[0];
  }

  private assignUserToVariant(
    userId: string,
    testId: string,
    variantId: string
  ): void {
    if (!this.userAssignments.has(userId)) {
      this.userAssignments.set(userId, new Map());
    }

    const userTests = this.userAssignments.get(userId)!;
    userTests.set(testId, {
      userId,
      testId,
      variantId,
      assignedAt: new Date(),
    });

    this.saveUserAssignments();
  }

  private getUserAssignment(
    userId: string,
    testId: string
  ): UserAssignment | undefined {
    return this.userAssignments.get(userId)?.get(testId);
  }

  private async trackExposure(
    testId: string,
    variantId: string,
    userId: string
  ): Promise<void> {
    const assignment = this.getUserAssignment(userId, testId);
    if (!assignment || assignment.exposedAt) {
      return; // Already tracked
    }

    assignment.exposedAt = new Date();

    // Send to backend
    await fetch('/api/v1/ab-testing/exposure', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        testId,
        variantId,
        userId,
        timestamp: new Date().toISOString(),
      }),
    });

    // Update local test data
    const test = this.activeTests.get(testId);
    if (test) {
      const variant = test.variants.find((v) => v.id === variantId);
      if (variant) {
        variant.exposures++;
        if (variant.conversions > 0) {
          variant.conversionRate = variant.conversions / variant.exposures;
        }
      }
    }
  }

  private matchesTargetAudience(audience: TargetAudience): boolean {
    // Check user type
    if (audience.userType && audience.userType !== 'all') {
      // Would check actual user type from auth context
      // For now, assume match
    }

    // Check device type
    if (audience.deviceType && audience.deviceType !== 'all') {
      const isMobile = /iPhone|iPad|iPod|Android/i.test(navigator.userAgent);
      const isTablet = /iPad|Android/i.test(navigator.userAgent) && window.innerWidth >= 768;
      const currentDevice = isTablet ? 'tablet' : isMobile ? 'mobile' : 'desktop';

      if (currentDevice !== audience.deviceType) {
        return false;
      }
    }

    // Check new vs returning users
    const isNewUser = !localStorage.getItem('user_visited');
    if (audience.newUsers && !isNewUser) {
      return false;
    }
    if (audience.returningUsers && isNewUser) {
      return false;
    }

    return true;
  }

  private getUserId(): string {
    let userId = localStorage.getItem('anonymous_user_id');
    if (!userId) {
      userId = this.generateUUID();
      localStorage.setItem('anonymous_user_id', userId);
    }
    return userId;
  }

  private saveUserAssignments(): void {
    const assignments: Record<string, string> = {};
    this.userAssignments.get(this.getUserId())?.forEach((assignment, testId) => {
      assignments[testId] = assignment.variantId;
    });
    localStorage.setItem('ab_test_assignments', JSON.stringify(assignments));
  }

  private hashString(str: string): number {
    let hash = 0;
    for (let i = 0; i < str.length; i++) {
      const char = str.charCodeAt(i);
      hash = (hash << 5) - hash + char;
      hash = hash & hash; // Convert to 32-bit integer
    }
    return Math.abs(hash);
  }

  private normalCDF(x: number): number {
    // Approximation of cumulative distribution function for standard normal
    const t = 1 / (1 + 0.2316419 * Math.abs(x));
    const d = 0.3989423 * Math.exp((-x * x) / 2);
    const prob =
      d *
      t *
      (0.3193815 +
        t * (-0.3565638 + t * (1.781478 + t * (-1.821256 + t * 1.330274))));

    return x > 0 ? 1 - prob : prob;
  }

  private generateUUID(): string {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, (c) => {
      const r = (Math.random() * 16) | 0;
      const v = c === 'x' ? r : (r & 0x3) | 0x8;
      return v.toString(16);
    });
  }
}

// Singleton instance
export const abTestingService = new ABTestingService();

// React Hook
export function useABTest(testId: string) {
  const [variant, setVariant] = React.useState<Variant | null>(null);

  React.useEffect(() => {
    abTestingService.initialize().then(() => {
      const assignedVariant = abTestingService.getVariant(testId);
      setVariant(assignedVariant);
    });
  }, [testId]);

  const trackConversion = React.useCallback(
    (metricId: string, value?: number) => {
      return abTestingService.trackConversion(testId, metricId, value);
    },
    [testId]
  );

  const trackEvent = React.useCallback(
    (eventName: string, properties?: Record<string, any>) => {
      return abTestingService.trackEvent(testId, eventName, properties);
    },
    [testId]
  );

  const getConfig = React.useCallback(
    <T = any>(key: string, defaultValue: T): T => {
      return abTestingService.getVariantConfig(testId, key, defaultValue);
    },
    [testId, variant]
  );

  return {
    variant,
    isActive: !!variant,
    variantId: variant?.id,
    trackConversion,
    trackEvent,
    getConfig,
  };
}

// Component wrapper
export function ABTestVariant({
  testId,
  variantId,
  children,
}: {
  testId: string;
  variantId: string;
  children: React.ReactNode;
}) {
  const { variantId: activeVariantId } = useABTest(testId);

  if (activeVariantId !== variantId) {
    return null;
  }

  return <>{children}</>;
}

// Export for use in other files
import React from 'react';
export default abTestingService;
