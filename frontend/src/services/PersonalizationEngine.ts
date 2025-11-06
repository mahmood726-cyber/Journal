/**
 * Personalization Engine
 *
 * AI-powered personalization system:
 * - User profiling (interests, behavior, reading patterns)
 * - Content recommendations
 * - Personalized homepage
 * - Smart notifications
 * - Adaptive UI
 * - Reading history tracking
 */

export interface UserProfile {
  userId: string;
  interests: Interest[];
  readingHistory: ReadingHistoryItem[];
  preferences: UserPreferences;
  behavior: UserBehavior;
  demographics: Demographics;
  lastUpdated: Date;
}

export interface Interest {
  topic: string;
  weight: number; // 0-1, higher = more interested
  source: 'explicit' | 'implicit'; // User selected or inferred
  updatedAt: Date;
}

export interface ReadingHistoryItem {
  articleId: string;
  articleTitle: string;
  topics: string[];
  viewedAt: Date;
  timeSpent: number; // seconds
  scrollDepth: number; // 0-100%
  completed: boolean;
  saved: boolean;
  shared: boolean;
}

export interface UserPreferences {
  emailFrequency: 'daily' | 'weekly' | 'monthly' | 'never';
  notificationTopics: string[];
  uiTheme: 'light' | 'dark' | 'auto';
  language: string;
  articleView: 'list' | 'grid' | 'compact';
  autoplay: boolean;
}

export interface UserBehavior {
  averageReadingTime: number; // seconds
  preferredReadingTime: 'morning' | 'afternoon' | 'evening' | 'night';
  devicePreference: 'desktop' | 'mobile' | 'tablet';
  engagementLevel: 'low' | 'medium' | 'high';
  lastVisit: Date;
  visitFrequency: number; // visits per week
  searchQueries: string[];
}

export interface Demographics {
  role: 'author' | 'reviewer' | 'reader' | 'editor' | 'student';
  institution?: string;
  country?: string;
  researchArea?: string[];
}

export interface Recommendation {
  id: string;
  type: 'article' | 'issue' | 'topic' | 'author' | 'event';
  title: string;
  description: string;
  relevanceScore: number; // 0-1
  reasons: string[];
  metadata: Record<string, any>;
}

export interface PersonalizedContent {
  recommendations: Recommendation[];
  trendingForYou: Recommendation[];
  continueReading: ReadingHistoryItem[];
  suggestedAuthors: string[];
  suggestedTopics: string[];
}

class PersonalizationEngine {
  private profile: UserProfile | null = null;
  private isInitialized = false;

  /**
   * Initialize personalization engine
   */
  async initialize(userId: string): Promise<void> {
    if (this.isInitialized) return;

    try {
      // Load user profile from backend
      const response = await fetch(`/api/v1/personalization/profile/${userId}`);
      if (response.ok) {
        this.profile = await response.json();
      } else {
        // Create new profile
        this.profile = this.createDefaultProfile(userId);
        await this.saveProfile();
      }

      this.isInitialized = true;

      // Start background tracking
      this.startBackgroundTracking();
    } catch (error) {
      console.error('Failed to initialize personalization:', error);
      this.profile = this.createDefaultProfile(userId);
    }
  }

  /**
   * Get personalized recommendations
   */
  async getRecommendations(limit: number = 10): Promise<Recommendation[]> {
    if (!this.profile) {
      return [];
    }

    try {
      const response = await fetch('/api/v1/personalization/recommendations', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          userId: this.profile.userId,
          interests: this.profile.interests,
          readingHistory: this.profile.readingHistory.slice(-20), // Recent 20
          limit,
        }),
      });

      const recommendations = await response.json();
      return recommendations;
    } catch (error) {
      console.error('Failed to fetch recommendations:', error);
      return [];
    }
  }

  /**
   * Get personalized content for homepage
   */
  async getPersonalizedHomepage(): Promise<PersonalizedContent> {
    if (!this.profile) {
      return this.getDefaultContent();
    }

    try {
      const response = await fetch('/api/v1/personalization/homepage', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          userId: this.profile.userId,
          profile: this.profile,
        }),
      });

      const content = await response.json();
      return content;
    } catch (error) {
      console.error('Failed to fetch personalized homepage:', error);
      return this.getDefaultContent();
    }
  }

  /**
   * Track article view
   */
  async trackArticleView(
    articleId: string,
    articleTitle: string,
    topics: string[],
    timeSpent: number,
    scrollDepth: number
  ): Promise<void> {
    if (!this.profile) return;

    const historyItem: ReadingHistoryItem = {
      articleId,
      articleTitle,
      topics,
      viewedAt: new Date(),
      timeSpent,
      scrollDepth,
      completed: scrollDepth > 80,
      saved: false,
      shared: false,
    };

    this.profile.readingHistory.push(historyItem);

    // Keep only last 100 items
    if (this.profile.readingHistory.length > 100) {
      this.profile.readingHistory = this.profile.readingHistory.slice(-100);
    }

    // Update interests based on topics
    this.updateInterestsFromTopics(topics, timeSpent, scrollDepth);

    // Update behavior metrics
    this.updateBehaviorMetrics(timeSpent);

    await this.saveProfile();
  }

  /**
   * Track search query
   */
  async trackSearch(query: string): Promise<void> {
    if (!this.profile) return;

    this.profile.behavior.searchQueries.push(query);

    // Keep only last 50 queries
    if (this.profile.behavior.searchQueries.length > 50) {
      this.profile.behavior.searchQueries = this.profile.behavior.searchQueries.slice(-50);
    }

    // Extract topics from query to update interests
    const topics = this.extractTopicsFromQuery(query);
    this.updateInterestsFromTopics(topics, 0, 0);

    await this.saveProfile();
  }

  /**
   * Update user preferences
   */
  async updatePreferences(preferences: Partial<UserPreferences>): Promise<void> {
    if (!this.profile) return;

    this.profile.preferences = {
      ...this.profile.preferences,
      ...preferences,
    };

    await this.saveProfile();
  }

  /**
   * Add explicit interest
   */
  async addInterest(topic: string): Promise<void> {
    if (!this.profile) return;

    const existing = this.profile.interests.find((i) => i.topic === topic);

    if (existing) {
      existing.weight = Math.min(existing.weight + 0.2, 1.0);
      existing.source = 'explicit';
      existing.updatedAt = new Date();
    } else {
      this.profile.interests.push({
        topic,
        weight: 0.8,
        source: 'explicit',
        updatedAt: new Date(),
      });
    }

    await this.saveProfile();
  }

  /**
   * Remove interest
   */
  async removeInterest(topic: string): Promise<void> {
    if (!this.profile) return;

    this.profile.interests = this.profile.interests.filter(
      (i) => i.topic !== topic
    );

    await this.saveProfile();
  }

  /**
   * Get user profile
   */
  getProfile(): UserProfile | null {
    return this.profile;
  }

  /**
   * Get engagement level
   */
  getEngagementLevel(): 'low' | 'medium' | 'high' {
    if (!this.profile) return 'low';
    return this.profile.behavior.engagementLevel;
  }

  /**
   * Get recommended notification topics
   */
  getRecommendedNotificationTopics(): string[] {
    if (!this.profile) return [];

    // Return top 5 interests
    return this.profile.interests
      .sort((a, b) => b.weight - a.weight)
      .slice(0, 5)
      .map((i) => i.topic);
  }

  /**
   * Predict user interest in topic
   */
  predictInterestInTopic(topic: string): number {
    if (!this.profile) return 0.5;

    const interest = this.profile.interests.find((i) => i.topic === topic);
    if (interest) {
      return interest.weight;
    }

    // Check for related topics in reading history
    const relatedReads = this.profile.readingHistory.filter((h) =>
      h.topics.includes(topic)
    ).length;

    if (relatedReads > 0) {
      return Math.min(relatedReads * 0.1, 0.7);
    }

    return 0.3; // Default low interest
  }

  /**
   * Get similar users (for collaborative filtering)
   */
  async getSimilarUsers(limit: number = 10): Promise<string[]> {
    if (!this.profile) return [];

    try {
      const response = await fetch('/api/v1/personalization/similar-users', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          userId: this.profile.userId,
          interests: this.profile.interests,
          limit,
        }),
      });

      const users = await response.json();
      return users;
    } catch (error) {
      console.error('Failed to fetch similar users:', error);
      return [];
    }
  }

  // ==================== Private Methods ====================

  private createDefaultProfile(userId: string): UserProfile {
    return {
      userId,
      interests: [],
      readingHistory: [],
      preferences: {
        emailFrequency: 'weekly',
        notificationTopics: [],
        uiTheme: 'auto',
        language: 'en',
        articleView: 'list',
        autoplay: false,
      },
      behavior: {
        averageReadingTime: 0,
        preferredReadingTime: 'afternoon',
        devicePreference: this.detectDevice(),
        engagementLevel: 'low',
        lastVisit: new Date(),
        visitFrequency: 0,
        searchQueries: [],
      },
      demographics: {
        role: 'reader',
      },
      lastUpdated: new Date(),
    };
  }

  private getDefaultContent(): PersonalizedContent {
    return {
      recommendations: [],
      trendingForYou: [],
      continueReading: [],
      suggestedAuthors: [],
      suggestedTopics: [],
    };
  }

  private updateInterestsFromTopics(
    topics: string[],
    timeSpent: number,
    scrollDepth: number
  ): void {
    if (!this.profile) return;

    // Calculate engagement score (0-1)
    const engagementScore =
      (Math.min(timeSpent / 300, 1) * 0.5 + scrollDepth / 100 * 0.5);

    topics.forEach((topic) => {
      const existing = this.profile!.interests.find((i) => i.topic === topic);

      if (existing) {
        // Update weight using exponential moving average
        existing.weight = existing.weight * 0.8 + engagementScore * 0.2;
        existing.weight = Math.min(existing.weight, 1.0);
        existing.updatedAt = new Date();
      } else {
        // Add new interest
        this.profile!.interests.push({
          topic,
          weight: engagementScore * 0.5, // Start lower for implicit interests
          source: 'implicit',
          updatedAt: new Date(),
        });
      }
    });

    // Decay old interests
    this.decayInterests();
  }

  private decayInterests(): void {
    if (!this.profile) return;

    const now = new Date();
    const oneMonth = 30 * 24 * 60 * 60 * 1000;

    this.profile.interests = this.profile.interests
      .map((interest) => {
        const age = now.getTime() - interest.updatedAt.getTime();
        const decayFactor = Math.exp(-age / oneMonth);

        return {
          ...interest,
          weight: interest.weight * decayFactor,
        };
      })
      .filter((interest) => interest.weight > 0.05); // Remove very low interests
  }

  private updateBehaviorMetrics(timeSpent: number): void {
    if (!this.profile) return;

    const history = this.profile.readingHistory;

    // Update average reading time
    const recentReads = history.slice(-20);
    const avgTime =
      recentReads.reduce((sum, h) => sum + h.timeSpent, 0) / recentReads.length;
    this.profile.behavior.averageReadingTime = avgTime;

    // Update engagement level
    const completedReads = recentReads.filter((h) => h.completed).length;
    const completionRate = completedReads / recentReads.length;

    if (completionRate > 0.7 && avgTime > 180) {
      this.profile.behavior.engagementLevel = 'high';
    } else if (completionRate > 0.4 || avgTime > 120) {
      this.profile.behavior.engagementLevel = 'medium';
    } else {
      this.profile.behavior.engagementLevel = 'low';
    }

    // Update preferred reading time
    const currentHour = new Date().getHours();
    if (currentHour < 12) {
      this.profile.behavior.preferredReadingTime = 'morning';
    } else if (currentHour < 17) {
      this.profile.behavior.preferredReadingTime = 'afternoon';
    } else if (currentHour < 21) {
      this.profile.behavior.preferredReadingTime = 'evening';
    } else {
      this.profile.behavior.preferredReadingTime = 'night';
    }
  }

  private extractTopicsFromQuery(query: string): string[] {
    // Simple topic extraction - in production would use NLP
    const commonWords = new Set([
      'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at',
      'to', 'for', 'of', 'with', 'by', 'from', 'as', 'is', 'was',
    ]);

    return query
      .toLowerCase()
      .split(/\s+/)
      .filter((word) => word.length > 3 && !commonWords.has(word));
  }

  private detectDevice(): 'desktop' | 'mobile' | 'tablet' {
    const ua = navigator.userAgent;
    if (/(tablet|ipad|playbook|silk)|(android(?!.*mobi))/i.test(ua)) {
      return 'tablet';
    }
    if (/Mobile|Android|iP(hone|od)|IEMobile|BlackBerry|Kindle|Silk-Accelerated|(hpw|web)OS|Opera M(obi|ini)/.test(ua)) {
      return 'mobile';
    }
    return 'desktop';
  }

  private async saveProfile(): Promise<void> {
    if (!this.profile) return;

    this.profile.lastUpdated = new Date();

    try {
      await fetch('/api/v1/personalization/profile', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(this.profile),
      });
    } catch (error) {
      console.error('Failed to save profile:', error);
    }
  }

  private startBackgroundTracking(): void {
    // Track page visibility
    document.addEventListener('visibilitychange', () => {
      if (document.hidden && this.profile) {
        this.saveProfile();
      }
    });

    // Track before unload
    window.addEventListener('beforeunload', () => {
      if (this.profile) {
        // Use sendBeacon for reliable tracking
        const blob = new Blob([JSON.stringify(this.profile)], {
          type: 'application/json',
        });
        navigator.sendBeacon('/api/v1/personalization/profile', blob);
      }
    });

    // Periodic sync (every 5 minutes)
    setInterval(() => {
      if (this.profile) {
        this.saveProfile();
      }
    }, 5 * 60 * 1000);
  }
}

// Singleton instance
export const personalizationEngine = new PersonalizationEngine();

// React Hook
export function usePersonalization() {
  const [profile, setProfile] = React.useState<UserProfile | null>(null);
  const [recommendations, setRecommendations] = React.useState<Recommendation[]>([]);
  const [isLoading, setIsLoading] = React.useState(true);

  React.useEffect(() => {
    const initialize = async () => {
      const userId = getUserIdFromAuth(); // Would get from auth context
      await personalizationEngine.initialize(userId);
      setProfile(personalizationEngine.getProfile());
      const recs = await personalizationEngine.getRecommendations();
      setRecommendations(recs);
      setIsLoading(false);
    };

    initialize();
  }, []);

  const trackArticleView = React.useCallback(
    async (
      articleId: string,
      articleTitle: string,
      topics: string[],
      timeSpent: number,
      scrollDepth: number
    ) => {
      await personalizationEngine.trackArticleView(
        articleId,
        articleTitle,
        topics,
        timeSpent,
        scrollDepth
      );
      setProfile(personalizationEngine.getProfile());
    },
    []
  );

  const trackSearch = React.useCallback(async (query: string) => {
    await personalizationEngine.trackSearch(query);
    setProfile(personalizationEngine.getProfile());
  }, []);

  const updatePreferences = React.useCallback(
    async (preferences: Partial<UserPreferences>) => {
      await personalizationEngine.updatePreferences(preferences);
      setProfile(personalizationEngine.getProfile());
    },
    []
  );

  const refreshRecommendations = React.useCallback(async () => {
    const recs = await personalizationEngine.getRecommendations();
    setRecommendations(recs);
  }, []);

  return {
    profile,
    recommendations,
    isLoading,
    trackArticleView,
    trackSearch,
    updatePreferences,
    refreshRecommendations,
  };
}

function getUserIdFromAuth(): string {
  // Would get from actual auth context
  return localStorage.getItem('user_id') || 'anonymous';
}

import React from 'react';
export default personalizationEngine;
