import React, { useState, useEffect, useCallback } from "react";
import { Plus, ChevronLeft, ChevronRight, Eye } from "lucide-react";
import { StoryViewer } from "../stories/StoryViewer";

interface Story {
  id: number;
  content: string;
  media_type?: string;
  media_url?: string;
  background_color?: string;
  author: {
    id: number;
    first_name: string;
    last_name: string;
    avatar?: string;
  };
  created_at: string;
  expires_at: string;
  views_count: number;
  has_viewed?: boolean; // Track if current user has viewed
  is_new?: boolean; // Track if story is new (less than 24h and not viewed)
}

interface StoriesBarProps {
  userToken: string;
  onCreateStory: () => void;
  currentUser: {
    id?: number;
    name: string;
    email: string;
    avatar?: string;
    token: string;
  };
  refreshTrigger?: number; // For triggering immediate updates
}

export const EnhancedStoriesBar: React.FC<StoriesBarProps> = ({
  userToken,
  onCreateStory,
  currentUser,
  refreshTrigger = 0,
}) => {
  const [stories, setStories] = useState<Story[]>([]);
  const [groupedStories, setGroupedStories] = useState<{
    [key: number]: Story[];
  }>({});
  const [selectedStoryGroup, setSelectedStoryGroup] = useState<Story[] | null>(
    null,
  );
  const [selectedStoryIndex, setSelectedStoryIndex] = useState(0);
  const [currentPage, setCurrentPage] = useState(0);
  const [isMobile, setIsMobile] = useState(false);
  const [viewedStories, setViewedStories] = useState<Set<number>>(new Set()); // Track viewed stories locally

  const storiesPerPage = isMobile ? 4 : 6;

  // Load viewed stories from localStorage
  useEffect(() => {
    const savedViewed = localStorage.getItem("viewedStories");
    if (savedViewed) {
      try {
        const parsed = JSON.parse(savedViewed);
        setViewedStories(new Set(parsed));
      } catch (error) {
        console.error("Error parsing viewed stories:", error);
      }
    }
  }, []);

  // Save viewed stories to localStorage
  const saveViewedStories = useCallback((viewed: Set<number>) => {
    localStorage.setItem("viewedStories", JSON.stringify(Array.from(viewed)));
  }, []);

  // Mark story as viewed
  const markStoryAsViewed = useCallback(
    (storyId: number) => {
      setViewedStories((prev) => {
        const newViewed = new Set(prev);
        newViewed.add(storyId);
        saveViewedStories(newViewed);
        return newViewed;
      });
    },
    [saveViewedStories],
  );

  // Check if story group has unread stories
  const hasUnreadStories = useCallback(
    (authorStories: Story[]) => {
      return authorStories.some((story) => {
        const isRecent =
          Date.now() - new Date(story.created_at).getTime() <
          24 * 60 * 60 * 1000;
        return isRecent && !viewedStories.has(story.id);
      });
    },
    [viewedStories],
  );

  useEffect(() => {
    fetchStories();

    const checkIfMobile = () => {
      setIsMobile(window.innerWidth < 768);
    };

    checkIfMobile();
    window.addEventListener("resize", checkIfMobile);
    return () => window.removeEventListener("resize", checkIfMobile);
  }, [refreshTrigger]); // Re-fetch when refreshTrigger changes

  useEffect(() => {
    // Group stories by author
    const grouped = stories.reduce(
      (acc, story) => {
        const authorId = story.author.id;
        if (!acc[authorId]) {
          acc[authorId] = [];
        }

        // Add read status to story
        const isRecent =
          Date.now() - new Date(story.created_at).getTime() <
          24 * 60 * 60 * 1000;
        const enhancedStory = {
          ...story,
          has_viewed: viewedStories.has(story.id),
          is_new: isRecent && !viewedStories.has(story.id),
        };

        acc[authorId].push(enhancedStory);
        return acc;
      },
      {} as { [key: number]: Story[] },
    );

    // Sort stories within each group by creation date
    Object.keys(grouped).forEach((authorId) => {
      grouped[parseInt(authorId)].sort(
        (a, b) =>
          new Date(a.created_at).getTime() - new Date(b.created_at).getTime(),
      );
    });

    setGroupedStories(grouped);
  }, [stories, viewedStories]);

  const fetchStories = async () => {
    try {
      const response = await fetch("http://localhost:8000/stories/", {
        headers: {
          Authorization: `Bearer ${userToken}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setStories(data);
      }
    } catch (error) {
      console.error("Erro ao carregar stories:", error);
    }
  };

  const handleViewStoryGroup = (authorId: number, storyIndex: number = 0) => {
    const authorStories = groupedStories[authorId];
    if (authorStories && authorStories.length > 0) {
      setSelectedStoryGroup(authorStories);
      setSelectedStoryIndex(storyIndex);

      // Mark the first story as viewed immediately
      if (authorStories[storyIndex]) {
        markStoryAsViewed(authorStories[storyIndex].id);
      }
    }
  };

  const handleDeleteStory = (storyId: string) => {
    const numId = parseInt(storyId);
    setStories((prev) => prev.filter((story) => story.id !== numId));

    // Remove from viewed stories if it was there
    setViewedStories((prev) => {
      const newViewed = new Set(prev);
      newViewed.delete(numId);
      saveViewedStories(newViewed);
      return newViewed;
    });

    // If the deleted story was the last one in the group, close the viewer
    if (selectedStoryGroup) {
      const updatedGroup = selectedStoryGroup.filter(
        (story) => story.id !== numId,
      );
      if (updatedGroup.length === 0) {
        setSelectedStoryGroup(null);
      } else {
        setSelectedStoryGroup(updatedGroup);
        // Adjust index if necessary
        if (selectedStoryIndex >= updatedGroup.length) {
          setSelectedStoryIndex(updatedGroup.length - 1);
        }
      }
    }
  };

  const handleStoryView = (storyId: string) => {
    markStoryAsViewed(parseInt(storyId));
  };

  const getStoryPreview = (authorStories: Story[]) => {
    const latestStory = authorStories[authorStories.length - 1];

    if (latestStory.media_type === "photo" && latestStory.media_url) {
      return (
        <img
          src={latestStory.media_url}
          alt="Story preview"
          className="w-full h-full object-cover"
          onError={(e) => {
            console.error(
              "Erro ao carregar imagem do story:",
              latestStory.media_url,
            );
            // Fallback to content preview
            const target = e.currentTarget;
            target.style.display = "none";
            const parent = target.parentElement;
            if (parent) {
              parent.innerHTML = `
                <div style="width: 100%; height: 100%; display: flex; align-items: center; justify-content: center; background-color: ${latestStory.background_color || "#3B82F6"}; color: white; font-size: 12px; padding: 4px;">
                  <span style="text-align: center; line-height: 1.2;">
                    ${latestStory.content?.substring(0, 10) || "📷"}
                    ${latestStory.content && latestStory.content.length > 10 ? "..." : ""}
                  </span>
                </div>
              `;
            }
          }}
        />
      );
    }

    if (latestStory.media_type === "video" && latestStory.media_url) {
      return (
        <div className="w-full h-full bg-gray-800 flex items-center justify-center">
          <span className="text-white text-2xl">📹</span>
        </div>
      );
    }

    if (latestStory.media_type === "music" && latestStory.media_url) {
      return (
        <div
          className="w-full h-full flex items-center justify-center"
          style={{ backgroundColor: latestStory.background_color || "#3B82F6" }}
        >
          <span className="text-white text-2xl">🎵</span>
        </div>
      );
    }

    return (
      <div
        className="w-full h-full flex items-center justify-center text-white text-xs font-medium p-1"
        style={{ backgroundColor: latestStory.background_color || "#3B82F6" }}
      >
        <span className="text-center leading-tight">
          {latestStory.content?.substring(0, 10) || "📝"}
          {latestStory.content && latestStory.content.length > 10 && "..."}
        </span>
      </div>
    );
  };

  const uniqueAuthors = Object.keys(groupedStories).map((id) => parseInt(id));

  // Sort authors: unread stories first, then by most recent story
  const sortedAuthors = uniqueAuthors.sort((a, b) => {
    const aStories = groupedStories[a];
    const bStories = groupedStories[b];

    const aHasUnread = hasUnreadStories(aStories);
    const bHasUnread = hasUnreadStories(bStories);

    // Unread stories first
    if (aHasUnread && !bHasUnread) return -1;
    if (!aHasUnread && bHasUnread) return 1;

    // Then by most recent story
    const aLatest = Math.max(
      ...aStories.map((s) => new Date(s.created_at).getTime()),
    );
    const bLatest = Math.max(
      ...bStories.map((s) => new Date(s.created_at).getTime()),
    );

    return bLatest - aLatest;
  });

  const totalPages = Math.ceil(sortedAuthors.length / storiesPerPage);
  const currentAuthors = sortedAuthors.slice(
    currentPage * storiesPerPage,
    (currentPage + 1) * storiesPerPage,
  );

  const nextPage = () => {
    if (currentPage < totalPages - 1) {
      setCurrentPage((prev) => prev + 1);
    }
  };

  const prevPage = () => {
    if (currentPage > 0) {
      setCurrentPage((prev) => prev - 1);
    }
  };

  return (
    <>
      <div className="bg-white rounded-xl shadow-sm p-3 md:p-4">
        <div className="flex items-center justify-between mb-3 md:mb-4">
          <h3 className="font-semibold text-gray-900 text-sm md:text-base">Stories</h3>
          <div className="flex items-center space-x-1 md:space-x-2">
            {totalPages > 1 && (
              <>
                <button
                  onClick={prevPage}
                  disabled={currentPage === 0}
                  className="p-1.5 md:p-2 rounded-full hover:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  <ChevronLeft className="w-3 h-3 md:w-4 md:h-4" />
                </button>
                <span className="text-xs md:text-sm text-gray-500 px-1 md:px-2">
                  {currentPage + 1} / {totalPages}
                </span>
                <button
                  onClick={nextPage}
                  disabled={currentPage === totalPages - 1}
                  className="p-1.5 md:p-2 rounded-full hover:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  <ChevronRight className="w-3 h-3 md:w-4 md:h-4" />
                </button>
              </>
            )}
          </div>
        </div>

        <div className="flex space-x-3 md:space-x-4 overflow-x-auto pb-2 md:pb-0">
          {/* Add Story Button */}
          <button
            onClick={onCreateStory}
            className="flex-shrink-0 flex flex-col items-center space-y-1 md:space-y-2 group"
          >
            <div className="w-12 h-12 md:w-16 md:h-16 bg-gradient-to-br from-purple-500 to-pink-500 rounded-full flex items-center justify-center group-hover:scale-105 transition-transform">
              <Plus className="w-5 h-5 md:w-8 md:h-8 text-white" />
            </div>
            <span className="text-xs text-gray-600 font-medium">Seu story</span>
          </button>

          {/* Stories */}
          {currentAuthors.map((authorId) => {
            const authorStories = groupedStories[authorId];
            const author = authorStories[0].author;
            const totalViews = authorStories.reduce(
              (sum, story) => sum + story.views_count,
              0,
            );
            const hasUnread = hasUnreadStories(authorStories);
            const unreadCount = authorStories.filter(
              (story) => story.is_new,
            ).length;

            return (
              <button
                key={authorId}
                onClick={() => handleViewStoryGroup(authorId)}
                className="flex-shrink-0 flex flex-col items-center space-y-2 group"
              >
                <div className="relative">
                  {/* Enhanced Story Aura - much more visible */}
                  <div
                    className={`w-12 h-12 md:w-16 md:h-16 rounded-full p-0.5 group-hover:scale-105 transition-all duration-300 ${
                      hasUnread
                        ? "bg-gradient-to-r from-purple-500 via-pink-500 to-red-500 shadow-lg animate-pulse"
                        : "bg-gray-300"
                    }`}
                    style={{
                      boxShadow: hasUnread
                        ? "0 0 0 2px rgba(236, 72, 153, 0.4), 0 0 0 4px rgba(147, 51, 234, 0.3), 0 0 20px rgba(147, 51, 234, 0.2)"
                        : "none",
                    }}
                  >
                    <div className="w-full h-full rounded-full overflow-hidden bg-white p-0.5">
                      <div className="w-full h-full rounded-full overflow-hidden bg-gray-200">
                        {getStoryPreview(authorStories)}
                      </div>
                    </div>
                  </div>

                  {/* Additional glow effect for unread stories */}
                  {hasUnread && (
                    <div className="absolute inset-0 w-16 h-16 rounded-full bg-gradient-to-r from-purple-500 via-pink-500 to-red-500 opacity-20 animate-ping pointer-events-none"></div>
                  )}

                  {/* Unread indicator */}
                  {hasUnread && unreadCount > 0 && (
                    <div className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center font-bold shadow-lg animate-pulse">
                      {unreadCount > 9 ? "9+" : unreadCount}
                    </div>
                  )}

                  {/* Story count indicator (when multiple stories) */}
                  {authorStories.length > 1 && !hasUnread && (
                    <div className="absolute -top-1 -right-1 bg-blue-500 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center font-bold shadow-lg">
                      {authorStories.length}
                    </div>
                  )}

                  {/* Views count for own stories */}
                  {authorId === currentUser.id && totalViews > 0 && (
                    <div className="absolute -bottom-1 -right-1 bg-green-500 w-4 h-4 rounded-full border-2 border-white flex items-center justify-center">
                      <Eye className="w-2 h-2 text-white" />
                    </div>
                  )}

                  {/* Read indicator */}
                  {!hasUnread && authorId !== currentUser.id && (
                    <div className="absolute -bottom-1 -right-1 bg-gray-400 w-4 h-4 rounded-full border-2 border-white flex items-center justify-center">
                      <span className="text-xs text-white">✓</span>
                    </div>
                  )}
                </div>
                <span
                  className={`text-xs max-w-16 truncate font-medium ${
                    hasUnread ? "text-gray-900 font-semibold" : "text-gray-600"
                  }`}
                >
                  {author.first_name}
                </span>
              </button>
            );
          })}

          {/* Empty state */}
          {uniqueAuthors.length === 0 && (
            <div className="flex-1 flex items-center justify-center py-8">
              <p className="text-gray-500 text-sm">
                Nenhum story ainda. Seja o primeiro!
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Story Viewer */}
      {selectedStoryGroup && (
        <StoryViewer
          stories={selectedStoryGroup.map((story) => ({
            ...story,
            id: story.id.toString(),
          }))}
          currentIndex={selectedStoryIndex}
          onClose={() => setSelectedStoryGroup(null)}
          userToken={userToken}
          onDelete={handleDeleteStory}
          currentUserId={currentUser.id}
          onView={handleStoryView} // Pass view handler
        />
      )}
    </>
  );
};
