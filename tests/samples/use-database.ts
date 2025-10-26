'use client';

import { useState, useEffect, useMemo, useCallback, useRef } from 'react';
import { db } from '@/lib/supabase/database';
import { useSupabase } from './use-supabase';
import type { SearchFilters, Agent, Category, Collection, SearchResult } from '@/types';

export function useAgents(filters: SearchFilters = {}) {
  const [agents, setAgents] = useState<Agent[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchAgents() {
      try {
        setLoading(true);
        setError(null);
        const query = await db.getAgents(filters);
        const { data, error: dbError } = await query;
        
        if (dbError) throw dbError;
        setAgents(data || []);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch agents');
      } finally {
        setLoading(false);
      }
    }

    fetchAgents();
  }, [filters.query, filters.category, filters.tags?.join(','), filters.language, filters.framework, filters.featured, filters.sortBy, filters.limit, filters.offset]);

  return { agents, loading, error, refetch: () => fetchAgents() };
}

export function useAgentSearch() {
  const [results, setResults] = useState<SearchResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Memoize the search function to prevent unnecessary re-renders
  const search = useCallback(async (filters: SearchFilters & { limit?: number; offset?: number }) => {
    try {
      setLoading(true);
      setError(null);
      const data = await db.searchAgents(filters);
      setResults(data);
    } catch (err) {
      console.error('Search error:', err);
      const errorMessage = err instanceof Error ? err.message : 'Search failed';
      
      // For timeout errors, provide a more user-friendly message
      if (errorMessage.includes('timeout')) {
        setError('Search is taking longer than expected. Please try simplifying your search or try again.');
      } else {
        setError(errorMessage);
      }
      
      // Set empty results on error instead of leaving old results
      setResults([]);
    } finally {
      setLoading(false);
    }
  }, []);

  return { results, loading, error, search };
}

// Debounced search hook for better performance with pagination support
export function useDebouncedAgentSearch(delay = 300) {
  const [results, setResults] = useState<SearchResult[]>([]);
  const [loading, setLoading] = useState(false); // Start with loading false - only show loading when actively searching
  const [error, setError] = useState<string | null>(null);
  const [lastBatchSize, setLastBatchSize] = useState(0); // Track size of last batch for hasMore logic
  const timeoutRef = useRef<NodeJS.Timeout>();
  const abortControllerRef = useRef<AbortController>();
  const hasSearchedRef = useRef(false); // Track if we've performed at least one search
  const lastFiltersRef = useRef<string>(''); // Track filter changes for pagination

  const debouncedSearch = useCallback(async (filters: SearchFilters & { limit?: number; offset?: number }) => {
    // Clear existing timeout
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }

    // Cancel previous request
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }

    // Don't search if query is too short (but allow empty queries for browsing)
    if (filters.query && filters.query.length > 0 && filters.query.length < 2) {
      setResults([]);
      setLoading(false);
      return;
    }

    // Create a key to detect if filters changed (excluding offset for pagination)
    const filtersKey = JSON.stringify({
      ...filters,
      offset: undefined // Exclude offset to detect actual filter changes
    });
    const isLoadMore = filters.offset && filters.offset > 0;
    const filtersChanged = filtersKey !== lastFiltersRef.current;

    // Always show loading for immediate feedback
    setLoading(true);
    setError(null);

    timeoutRef.current = setTimeout(async () => {
      try {
        setLoading(true);
        hasSearchedRef.current = true;
        
        // Create new abort controller for this request
        abortControllerRef.current = new AbortController();
        
        const data = await db.searchAgents(filters);
        setLastBatchSize(data.length);
        
        // If filters changed, replace results. If loading more, append results.
        if (filtersChanged || !isLoadMore) {
          setResults(data);
          lastFiltersRef.current = filtersKey;
        } else {
          // Load more: append new results to existing ones
          setResults(prev => [...prev, ...data]);
        }
      } catch (err: any) {
        // Don't set error if request was aborted - check multiple abort patterns
        if ((err instanceof Error && err.name === 'AbortError') ||
            err?.message?.includes('abort') || 
            err?.message?.includes('AbortError') ||
            err?.code === 'ABORT' ||
            err?.details?.includes('abort')) {
          return;
        }
        
        console.error('Debounced search error:', err);
        const errorMessage = err instanceof Error ? err.message : 'Search failed';
        
        if (errorMessage.includes('timeout')) {
          setError('Search is taking longer than expected. Please try simplifying your search or try again.');
        } else {
          setError(errorMessage);
        }
        
        // Only clear results if this is a new search, not load more
        if (filtersChanged || !isLoadMore) {
          setResults([]);
        }
      } finally {
        setLoading(false);
      }
    }, delay);
  }, [delay]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    };
  }, []);

  return { results, loading, error, search: debouncedSearch, lastBatchSize };
}

export function useAgent(id: string) {
  const [agent, setAgent] = useState<Agent | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchAgent() {
      if (!id) return;
      
      try {
        setLoading(true);
        setError(null);
        const data = await db.getAgentById(id);
        setAgent(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch agent');
      } finally {
        setLoading(false);
      }
    }

    fetchAgent();
  }, [id]);

  return { agent, loading, error, refetch: () => fetchAgent() };
}

// Simple cache for categories (they don't change often)
let cachedCategories: Category[] | null = null;
let categoriesCache: Promise<Category[]> | null = null;

export function useCategories() {
  const [categories, setCategories] = useState<Category[]>(cachedCategories || []);
  const [loading, setLoading] = useState(!cachedCategories);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchCategories() {
      // If we have cached data, use it
      if (cachedCategories) {
        setCategories(cachedCategories);
        setLoading(false);
        return;
      }

      // If there's already a request in flight, wait for it
      if (categoriesCache) {
        try {
          const data = await categoriesCache;
          setCategories(data);
          setLoading(false);
        } catch (err) {
          setError(err instanceof Error ? err.message : 'Failed to fetch categories');
          setLoading(false);
        }
        return;
      }

      try {
        setLoading(true);
        setError(null);
        
        // Create and cache the promise
        categoriesCache = db.getCategories();
        const data = await categoriesCache;
        
        // Cache the result
        cachedCategories = data;
        setCategories(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch categories');
        categoriesCache = null; // Clear failed cache
      } finally {
        setLoading(false);
      }
    }

    fetchCategories();
  }, []);

  return { categories, loading, error };
}

export function useUserCollections(userId?: string) {
  const [collections, setCollections] = useState<Collection[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchCollections() {
      if (!userId) {
        setCollections([]);
        setLoading(false);
        return;
      }

      try {
        setLoading(true);
        setError(null);
        const data = await db.getUserCollections(userId, true);
        setCollections(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch collections');
      } finally {
        setLoading(false);
      }
    }

    fetchCollections();
  }, [userId]);

  return { collections, loading, error };
}

export function useBookmarks() {
  const { user } = useSupabase();
  const [bookmarks, setBookmarks] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchBookmarks() {
      if (!user?.id) {
        setBookmarks([]);
        setLoading(false);
        return;
      }

      try {
        setLoading(true);
        setError(null);
        const data = await db.getUserBookmarks(user.id);
        setBookmarks(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch bookmarks');
      } finally {
        setLoading(false);
      }
    }

    fetchBookmarks();
  }, [user?.id]);

  const toggleBookmark = useCallback(async (agentId: string) => {
    if (!user?.id) return;

    try {
      const result = await db.toggleBookmark(user.id, agentId);
      // Refetch bookmarks to update the list
      const data = await db.getUserBookmarks(user.id);
      setBookmarks(data);
      return result;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to toggle bookmark');
      throw err;
    }
  }, [user?.id]);

  return { bookmarks, loading, error, toggleBookmark };
}

export function useVoting() {
  const { user } = useSupabase();
  const [error, setError] = useState<string | null>(null);

  const vote = async (
    voteType: 'upvote' | 'downvote',
    agentId?: string,
    reviewId?: string
  ) => {
    if (!user?.id) throw new Error('Must be logged in to vote');

    try {
      setError(null);
      const result = await db.toggleVote(user.id, voteType, agentId, reviewId);
      return result;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to vote';
      setError(errorMessage);
      throw new Error(errorMessage);
    }
  };

  const getUserVote = async (agentId?: string, reviewId?: string) => {
    if (!user?.id) return null;

    try {
      const vote = await db.getUserVote(user.id, agentId, reviewId);
      return vote;
    } catch (err) {
      console.warn('Failed to get user vote:', err);
      return null;
    }
  };

  return { vote, getUserVote, error };
}

export function useAgentMutations() {
  const { user } = useSupabase();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const createAgent = async (agentData: Partial<Agent>) => {
    if (!user?.id) throw new Error('Must be logged in');
    
    try {
      setLoading(true);
      setError(null);
      const data = await db.createAgent({ ...agentData, author_id: user.id });
      return data;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to create agent';
      setError(errorMessage);
      throw new Error(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const updateAgent = async (id: string, updates: Partial<Agent>) => {
    if (!user?.id) throw new Error('Must be logged in');
    
    try {
      setLoading(true);
      setError(null);
      
      // Check ownership
      const isOwner = await db.checkAgentOwnership(id, user.id);
      if (!isOwner) throw new Error('You can only edit your own agents');
      
      const data = await db.updateAgent(id, updates);
      return data;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to update agent';
      setError(errorMessage);
      throw new Error(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const deleteAgent = useCallback(async (id: string) => {
    if (!user?.id) throw new Error('Must be logged in');
    
    try {
      setLoading(true);
      setError(null);
      
      // Check ownership
      const isOwner = await db.checkAgentOwnership(id, user.id);
      if (!isOwner) throw new Error('You can only delete your own agents');
      
      await db.deleteAgent(id);
      return true;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to delete agent';
      setError(errorMessage);
      throw new Error(errorMessage);
    } finally {
      setLoading(false);
    }
  }, [user?.id]);

  const saveDraft = async (agentData: Partial<Agent>) => {
    if (!user?.id) throw new Error('Must be logged in');
    
    try {
      setLoading(true);
      setError(null);
      const data = await db.saveDraft(agentData, user.id);
      return data;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to save draft';
      setError(errorMessage);
      throw new Error(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const publishAgent = async (id: string) => {
    if (!user?.id) throw new Error('Must be logged in');
    
    try {
      setLoading(true);
      setError(null);
      
      // Check ownership
      const isOwner = await db.checkAgentOwnership(id, user.id);
      if (!isOwner) throw new Error('You can only publish your own agents');
      
      const data = await db.publishAgent(id);
      return data;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to publish agent';
      setError(errorMessage);
      throw new Error(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const duplicateAgent = useCallback(async (agentId: string) => {
    if (!user?.id) throw new Error('Must be logged in');
    
    try {
      setLoading(true);
      setError(null);
      const data = await db.duplicateAgent(agentId, user.id);
      return data;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to duplicate agent';
      setError(errorMessage);
      throw new Error(errorMessage);
    } finally {
      setLoading(false);
    }
  }, [user?.id]);

  return {
    createAgent,
    updateAgent,
    deleteAgent,
    saveDraft,
    publishAgent,
    duplicateAgent,
    loading,
    error
  };
}

export function useUserAgents(userId?: string) {
  const [agents, setAgents] = useState<Agent[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchUserAgents() {
      if (!userId) {
        setAgents([]);
        setLoading(false);
        return;
      }

      try {
        setLoading(true);
        setError(null);
        const data = await db.getUserAgents(userId, true);
        setAgents(data || []);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch user agents');
      } finally {
        setLoading(false);
      }
    }

    fetchUserAgents();
  }, [userId]);

  return { agents, loading, error, refetch: () => fetchUserAgents() };
}

export function useRelatedAgents(agentId?: string) {
  const [agents, setAgents] = useState<Agent[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchRelatedAgents() {
      if (!agentId) {
        setAgents([]);
        setLoading(false);
        return;
      }

      try {
        setLoading(true);
        setError(null);
        const data = await db.getRelatedAgents(agentId);
        setAgents(data || []);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch related agents');
      } finally {
        setLoading(false);
      }
    }

    fetchRelatedAgents();
  }, [agentId]);

  return { agents, loading, error };
}

export function useAnalytics() {
  const trackView = useCallback(async (agentId: string, sessionId?: string) => {
    try {
      await db.trackAgentView(agentId, undefined, sessionId, {
        userAgent: navigator.userAgent,
        referrer: document.referrer
      });
    } catch (err) {
      console.warn('Failed to track view:', err);
    }
  }, []);

  const trackDownload = useCallback(async (agentId: string, downloadType = 'direct') => {
    try {
      await db.trackAgentDownload(agentId, undefined, downloadType, {
        userAgent: navigator.userAgent,
        referrer: document.referrer
      });
    } catch (err) {
      console.warn('Failed to track download:', err);
    }
  }, []);

  return { trackView, trackDownload };
}

interface AgentPerformanceMetrics {
  views: number;
  downloads: number;
  bookmarks: number;
  reviews: number;
  average_rating: number;
  performance_score: number;
}

export function useAgentPerformanceMetrics(agentId?: string, days = 30) {
  const [metrics, setMetrics] = useState<AgentPerformanceMetrics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let isCancelled = false;

    async function fetchMetrics() {
      if (!agentId) {
        if (!isCancelled) {
          setMetrics(null);
          setLoading(false);
        }
        return;
      }

      try {
        setLoading(true);
        setError(null);
        const data = await db.getAgentPerformanceMetrics(agentId, days);
        if (!isCancelled) {
          setMetrics(data);
        }
      } catch (err) {
        if (!isCancelled) {
          setError(err instanceof Error ? err.message : 'Failed to fetch metrics');
        }
      } finally {
        if (!isCancelled) {
          setLoading(false);
        }
      }
    }

    fetchMetrics();

    return () => {
      isCancelled = true;
    };
  }, [agentId, days]);

  return { metrics, loading, error };
}

export function useSearchFacets(query?: string) {
  const [facets, setFacets] = useState<any>(null);
  const [loading, setLoading] = useState(false); // Start with loading false to show fallback data immediately
  const [error, setError] = useState<string | null>(null);
  const [hasEverLoaded, setHasEverLoaded] = useState(false);

  // Memoize facets to prevent unnecessary re-fetching
  const memoizedFacets = useMemo(() => {
    if (!facets) {
      // Return comprehensive fallback facets immediately to prevent empty UI
      return { 
        categories: [
          { value: 'Web Development', count: 0 },
          { value: 'Data Processing', count: 0 },
          { value: 'AI & ML', count: 0 },
          { value: 'API Tools', count: 0 },
          { value: 'Testing', count: 0 }
        ], 
        languages: [
          { value: 'JavaScript', count: 0 },
          { value: 'Python', count: 0 },
          { value: 'TypeScript', count: 0 },
          { value: 'Go', count: 0 },
          { value: 'Rust', count: 0 }
        ], 
        frameworks: [], 
        tags: [
          { value: 'automation', count: 0 },
          { value: 'development', count: 0 },
          { value: 'productivity', count: 0 },
          { value: 'testing', count: 0 }
        ]
      };
    }
    return facets;
  }, [facets]);

  useEffect(() => {
    let isCancelled = false;
    
    async function fetchFacets() {
      const startTime = Date.now();
      
      try {
        // Only show loading state if we've never successfully loaded before, and only briefly
        if (!hasEverLoaded) {
          setLoading(true);
        }
        setError(null);
        console.debug('useSearchFacets: Starting facets fetch...');
        
        // Load facets without aggressive timeout
        const data = await db.getSearchFacets(query);
        
        if (!isCancelled) {
          const duration = Date.now() - startTime;
          console.debug(`useSearchFacets: Facets loaded successfully in ${duration}ms`);
          setFacets(data);
          setHasEverLoaded(true);
        }
      } catch (err) {
        if (!isCancelled) {
          const duration = Date.now() - startTime;
          console.error(`useSearchFacets: Facets error after ${duration}ms:`, {
            error: err?.message || err?.toString() || 'Unknown error',
            errorType: typeof err,
            duration
          });
          
          const errorMessage = err instanceof Error ? err.message : 'Failed to fetch search facets';
          
          if (errorMessage.includes('timeout')) {
            // Don't show error for timeout - just use fallbacks silently
            console.warn('useSearchFacets: Using fallback facets due to timeout');
          } else {
            setError(`Filter loading error: ${errorMessage}`);
          }
          
          // Use the same comprehensive fallback as the memoized version
          const fallbackFacets = {
            categories: [
              { value: 'Web Development', count: 0 },
              { value: 'Data Processing', count: 0 },
              { value: 'AI & ML', count: 0 },
              { value: 'API Tools', count: 0 },
              { value: 'Testing', count: 0 }
            ],
            languages: [
              { value: 'JavaScript', count: 0 },
              { value: 'Python', count: 0 },
              { value: 'TypeScript', count: 0 },
              { value: 'Go', count: 0 },
              { value: 'Rust', count: 0 }
            ],
            frameworks: [],
            tags: [
              { value: 'automation', count: 0 },
              { value: 'development', count: 0 },
              { value: 'productivity', count: 0 },
              { value: 'testing', count: 0 }
            ]
          };
          setFacets(fallbackFacets);
        }
      } finally {
        if (!isCancelled) {
          setLoading(false);
        }
      }
    }

    fetchFacets();
    
    return () => {
      isCancelled = true;
    };
  }, [query]);

  return { facets: memoizedFacets, loading, error };
}

export function useBulkAgentOperations() {
  const { user } = useSupabase();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const bulkUpdate = async (agentIds: string[], updates: Partial<Agent>) => {
    if (!user?.id) throw new Error('Must be logged in');

    try {
      setLoading(true);
      setError(null);
      const data = await db.bulkUpdateAgents(agentIds, updates);
      return data;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Bulk update failed';
      setError(errorMessage);
      throw new Error(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const bulkDelete = async (agentIds: string[]) => {
    if (!user?.id) throw new Error('Must be logged in');

    try {
      setLoading(true);
      setError(null);
      await db.bulkDeleteAgents(agentIds);
      return true;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Bulk delete failed';
      setError(errorMessage);
      throw new Error(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const bulkAddToCollection = async (collectionId: string, agentIds: string[]) => {
    if (!user?.id) throw new Error('Must be logged in');

    try {
      setLoading(true);
      setError(null);
      const data = await db.bulkAddToCollection(collectionId, agentIds);
      return data;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to add to collection';
      setError(errorMessage);
      throw new Error(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  return {
    bulkUpdate,
    bulkDelete,
    bulkAddToCollection,
    loading,
    error
  };
}

interface AgentVersionHistory {
  id: string;
  agent_id: string;
  version_number: string;
  changes: string;
  created_at: string;
}

export function useAgentVersionHistory(agentId?: string) {
  const [versions, setVersions] = useState<AgentVersionHistory[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let isCancelled = false;

    async function fetchVersions() {
      if (!agentId) {
        if (!isCancelled) {
          setVersions([]);
          setLoading(false);
        }
        return;
      }

      try {
        setLoading(true);
        setError(null);
        const data = await db.getAgentVersionHistory(agentId);
        if (!isCancelled) {
          setVersions(data || []);
        }
      } catch (err) {
        if (!isCancelled) {
          setError(err instanceof Error ? err.message : 'Failed to fetch version history');
        }
      } finally {
        if (!isCancelled) {
          setLoading(false);
        }
      }
    }

    fetchVersions();

    return () => {
      isCancelled = true;
    };
  }, [agentId]);

  return { versions, loading, error };
}

// User dashboard data hook
export function useUserDashboard(userId?: string) {
  // Basic implementation
  const [data, setData] = useState<{
    stats: {
      totalAgents: number;
      totalDownloads: number;
      totalViews: number;
      totalCollections: number;
    };
    recentAgents: any[];
    recentCollections: any[];
  } | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!userId) return;

    async function fetchDashboardData() {
      try {
        setLoading(true);
        setError(null);

        // Get user agents and collections
        const [agents, collections] = await Promise.all([
          db.getUserAgents(userId, false),
          db.getUserCollections(userId, false)
        ]);

        // Calculate stats
        const stats = {
          totalAgents: agents.length,
          totalDownloads: agents.reduce((sum: number, agent: any) => sum + (agent.download_count || 0), 0),
          totalViews: agents.reduce((sum: number, agent: any) => sum + (agent.view_count || 0), 0),
          totalCollections: collections.length
        };

        setData({
          stats,
          recentAgents: agents.slice(0, 5),
          recentCollections: collections.slice(0, 5)
        });

      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch dashboard data');
        
        // Set default data on error
        setData({
          stats: {
            totalAgents: 0,
            totalDownloads: 0,
            totalViews: 0,
            totalCollections: 0
          },
          recentAgents: [],
          recentCollections: []
        });
      } finally {
        setLoading(false);
      }
    }

    fetchDashboardData();
  }, [userId]);

  return { data, loading, error, refetch: () => {} };
}

// User bookmarks hook
export function useUserBookmarks(userId?: string) {
  // Basic implementation
  const [bookmarks, setBookmarks] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchBookmarks = useCallback(async () => {
    if (!userId) return;

    try {
      setLoading(true);
      setError(null);

      const data = await db.getUserBookmarks(userId);
      setBookmarks(data || []);

    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch bookmarks');
      setBookmarks([]);
    } finally {
      setLoading(false);
    }
  }, [userId]);

  useEffect(() => {
    fetchBookmarks();
  }, [fetchBookmarks]);

  return { bookmarks, loading, error, refetch: fetchBookmarks };
}