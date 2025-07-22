import React, { useState, useEffect, useRef } from "react";
import { Plus, ChevronLeft, ChevronRight, Camera, Video } from "lucide-react";
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
}

interface ModernStoriesBarProps {
  userToken: string;
  onCreateStory: () => void;
  currentUser: {
    id?: number;
    name: string;
    email: string;
    avatar?: string;
    token: string;
  };
}

export const ModernStoriesBar: React.FC<ModernStoriesBarProps> = ({
  userToken,
  onCreateStory,
  currentUser,
}) => {
  const [stories, setStories] = useState<Story[]>([]);
  const [groupedStories, setGroupedStories] = useState<{
    [key: number]: Story[];
  }>({});
  const [selectedStoryGroup, setSelectedStoryGroup] = useState<Story[] | null>(
    null,
  );
  const [selectedStoryIndex, setSelectedStoryIndex] = useState(0);
  const [isMobile, setIsMobile] = useState(false);
  const scrollContainerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    fetchStories();

    const checkIfMobile = () => {
      setIsMobile(window.innerWidth < 768);
    };

    checkIfMobile();
    window.addEventListener("resize", checkIfMobile);
    return () => window.removeEventListener("resize", checkIfMobile);
  }, []);

  useEffect(() => {
    // Group stories by author
    const grouped = stories.reduce(
      (acc, story) => {
        const authorId = story.author.id;
        if (!acc[authorId]) {
          acc[authorId] = [];
        }
        acc[authorId].push(story);
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
  }, [stories]);

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
    }
  };

  const handleDeleteStory = (storyId: string) => {
    setStories((prev) =>
      prev.filter((story) => story.id !== parseInt(storyId)),
    );

    if (selectedStoryGroup) {
      const updatedGroup = selectedStoryGroup.filter(
        (story) => story.id !== parseInt(storyId),
      );
      if (updatedGroup.length === 0) {
        setSelectedStoryGroup(null);
      } else {
        setSelectedStoryGroup(updatedGroup);
        if (selectedStoryIndex >= updatedGroup.length) {
          setSelectedStoryIndex(updatedGroup.length - 1);
        }
      }
    }
  };

  const getStoryPreview = (authorStories: Story[]) => {
    const latestStory = authorStories[authorStories.length - 1];

    if (latestStory.media_type === "photo" && latestStory.media_url) {
      return (
        <img
          src={latestStory.media_url}
          alt="Story preview"
          className="w-full h-full object-cover"
        />
      );
    }

    if (latestStory.media_type === "video" && latestStory.media_url) {
      return (
        <div className="w-full h-full bg-gradient-to-br from-purple-600 to-pink-600 flex items-center justify-center">
          <Video className="w-6 h-6 text-white" />
        </div>
      );
    }

    return (
      <div
        className="w-full h-full flex items-center justify-center text-white text-xs font-bold"
        style={{ backgroundColor: latestStory.background_color || "#3B82F6" }}
      >
        <span className="text-center leading-tight px-1">
          {latestStory.content?.substring(0, 12) || "📝"}
          {latestStory.content && latestStory.content.length > 12 && "..."}
        </span>
      </div>
    );
  };

  const scroll = (direction: "left" | "right") => {
    if (scrollContainerRef.current) {
      const scrollAmount = isMobile ? 200 : 300;
      const newScrollLeft =
        scrollContainerRef.current.scrollLeft +
        (direction === "left" ? -scrollAmount : scrollAmount);

      scrollContainerRef.current.scrollTo({
        left: newScrollLeft,
        behavior: "smooth",
      });
    }
  };

  const uniqueAuthors = Object.keys(groupedStories).map((id) => parseInt(id));
  const hasUserStory = uniqueAuthors.includes(currentUser.id || 0);

  if (isMobile) {
    // Mobile layout (Instagram/Facebook style)
    return (
      <>
        <div className="bg-white">
          <div className="flex overflow-x-auto py-4 px-4 space-x-3 scrollbar-hide">
            {/* Add Story Button - Mobile */}
            <div className="flex-shrink-0 relative">
              <button
                onClick={onCreateStory}
                className="relative flex flex-col items-center"
              >
                <div className="w-16 h-16 rounded-full overflow-hidden bg-gray-100 border-2 border-gray-200 flex items-center justify-center">
                  {currentUser.avatar ? (
                    <img
                      src={currentUser.avatar}
                      alt={currentUser.name}
                      className="w-full h-full object-cover"
                    />
                  ) : (
                    <div className="w-full h-full bg-gradient-to-br from-blue-500 to-purple-500 flex items-center justify-center text-white font-bold text-lg">
                      {currentUser.name.charAt(0)}
                    </div>
                  )}
                </div>

                {/* Plus icon overlay */}
                <div className="absolute bottom-0 right-0 w-6 h-6 bg-blue-500 border-2 border-white rounded-full flex items-center justify-center">
                  <Plus className="w-3 h-3 text-white" />
                </div>

                <span className="text-xs text-gray-700 mt-1 text-center max-w-16 truncate">
                  Seu story
                </span>
              </button>
            </div>

            {/* Stories - Mobile */}
            {uniqueAuthors
              .filter((id) => id !== currentUser.id)
              .map((authorId) => {
                const authorStories = groupedStories[authorId];
                const author = authorStories[0].author;

                return (
                  <div key={authorId} className="flex-shrink-0 relative">
                    <button
                      onClick={() => handleViewStoryGroup(authorId)}
                      className="flex flex-col items-center"
                    >
                      {/* Story ring and preview */}
                      <div className="relative">
                        <div className="w-16 h-16 rounded-full p-0.5 bg-gradient-to-tr from-yellow-400 via-red-500 to-purple-600">
                          <div className="w-full h-full rounded-full overflow-hidden border-2 border-white bg-gray-200">
                            {getStoryPreview(authorStories)}
                          </div>
                        </div>

                        {/* Multiple stories indicator */}
                        {authorStories.length > 1 && (
                          <div className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center font-bold border-2 border-white">
                            {authorStories.length}
                          </div>
                        )}
                      </div>

                      <span className="text-xs text-gray-700 mt-1 text-center max-w-16 truncate">
                        {author.first_name}
                      </span>
                    </button>
                  </div>
                );
              })}
          </div>
        </div>

        {/* Story Viewer */}
        {selectedStoryGroup && (
          <StoryViewer
            stories={selectedStoryGroup}
            initialIndex={selectedStoryIndex}
            onClose={() => setSelectedStoryGroup(null)}
            userToken={userToken}
            currentUserId={currentUser.id}
            onStoryDeleted={handleDeleteStory}
          />
        )}
      </>
    );
  }

  // Desktop layout
  return (
    <>
      <div className="bg-white rounded-xl shadow-sm border border-gray-200">
        <div className="p-4">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-semibold text-gray-900 flex items-center">
              <Camera className="w-5 h-5 mr-2" />
              Stories
            </h3>

            {uniqueAuthors.length > 4 && (
              <div className="flex items-center space-x-2">
                <button
                  onClick={() => scroll("left")}
                  className="p-2 rounded-full hover:bg-gray-100 transition-colors"
                  aria-label="Scroll left"
                >
                  <ChevronLeft className="w-4 h-4" />
                </button>
                <button
                  onClick={() => scroll("right")}
                  className="p-2 rounded-full hover:bg-gray-100 transition-colors"
                  aria-label="Scroll right"
                >
                  <ChevronRight className="w-4 h-4" />
                </button>
              </div>
            )}
          </div>

          <div
            ref={scrollContainerRef}
            className="flex space-x-4 overflow-x-auto scrollbar-hide pb-2"
            style={{ scrollbarWidth: "none", msOverflowStyle: "none" }}
          >
            {/* Add Story Button - Desktop */}
            <div className="flex-shrink-0 group">
              <button
                onClick={onCreateStory}
                className="flex flex-col items-center space-y-2"
              >
                <div className="relative">
                  <div className="w-20 h-20 rounded-xl overflow-hidden bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center group-hover:scale-105 transition-transform">
                    <Plus className="w-8 h-8 text-white" />
                  </div>
                </div>
                <span className="text-xs text-gray-600 font-medium text-center max-w-20 truncate">
                  Criar story
                </span>
              </button>
            </div>

            {/* Stories - Desktop */}
            {uniqueAuthors.map((authorId) => {
              const authorStories = groupedStories[authorId];
              const author = authorStories[0].author;

              return (
                <div key={authorId} className="flex-shrink-0 group">
                  <button
                    onClick={() => handleViewStoryGroup(authorId)}
                    className="flex flex-col items-center space-y-2"
                  >
                    <div className="relative">
                      {/* Story ring */}
                      <div className="w-20 h-20 rounded-xl p-0.5 bg-gradient-to-tr from-yellow-400 via-red-500 to-purple-600 group-hover:scale-105 transition-transform">
                        <div className="w-full h-full rounded-xl overflow-hidden border-2 border-white bg-gray-200">
                          {getStoryPreview(authorStories)}
                        </div>
                      </div>

                      {/* Author avatar overlay */}
                      <div className="absolute -bottom-2 left-1/2 transform -translate-x-1/2">
                        <img
                          src={
                            author.avatar ||
                            `https://ui-avatars.com/api/?name=${encodeURIComponent(author.first_name + " " + author.last_name)}&background=3B82F6&color=fff&size=32`
                          }
                          alt={`${author.first_name} ${author.last_name}`}
                          className="w-8 h-8 rounded-full border-2 border-white shadow-lg"
                        />
                      </div>

                      {/* Multiple stories indicator */}
                      {authorStories.length > 1 && (
                        <div className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full w-6 h-6 flex items-center justify-center font-bold border-2 border-white">
                          {authorStories.length}
                        </div>
                      )}
                    </div>

                    <span className="text-xs text-gray-600 font-medium text-center max-w-20 truncate">
                      {author.first_name}
                    </span>
                  </button>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* Story Viewer */}
      {selectedStoryGroup && (
        <StoryViewer
          stories={selectedStoryGroup}
          initialIndex={selectedStoryIndex}
          onClose={() => setSelectedStoryGroup(null)}
          userToken={userToken}
          currentUserId={currentUser.id}
          onStoryDeleted={handleDeleteStory}
        />
      )}
    </>
  );
};
