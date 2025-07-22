import React, { useState, useEffect } from "react";
import {
  BrowserRouter as Router,
  Routes,
  Route,
  Navigate,
} from "react-router-dom";
import { Layout } from "./components/Layout";
import { EnhancedAuth } from "./components/auth/EnhancedAuth";
import { Feed } from "./components/Feed";
import { Profile } from "./components/profile/Profile";
import { ProfileRoute } from "./components/routing/ProfileRoute";
import { ChatPage } from "./components/chat/ChatPage";
import { NotificationCenter } from "./components/notifications/NotificationCenter";
import { notificationService } from "./services/NotificationService";

interface User {
  id?: number;
  name: string;
  email: string;
  username?: string;
  avatar?: string;
  bio?: string;
  location?: string;
  joinDate?: string;
  token: string;
}

function EnhancedApp() {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [realtimeNotifications, setRealtimeNotifications] = useState<any[]>([]);

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (token) {
      fetchUserData(token);
    } else {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (user?.id) {
      const handleNewNotification = (newNotification: any) => {
        setRealtimeNotifications((prev) => [newNotification, ...prev]);
      };

      const removeListener = notificationService.addListener(
        handleNewNotification,
      );
      notificationService.connect(user.id, user.token);

      return () => {
        removeListener();
        notificationService.disconnect();
      };
    }
  }, [user]);

  const fetchUserData = async (token: string) => {
    try {
      const response = await fetch("http://localhost:8000/auth/me", {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const userData = await response.json();
        const userWithDefaults = {
          id: userData.id,
          name: `${userData.first_name} ${userData.last_name}`,
          email: userData.email,
          username: userData.username || `user${userData.id}`,
          avatar: userData.avatar,
          bio:
            userData.bio || "Apaixonado por conexões genuínas e boas vibes! 🌟",
          location: userData.location || "São Paulo, Brasil",
          joinDate: userData.created_at
            ? new Date(userData.created_at).toLocaleDateString("pt-BR", {
                month: "long",
                year: "numeric",
              })
            : "Janeiro 2025",
          token,
        };
        setUser(userWithDefaults);
      } else {
        localStorage.removeItem("token");
      }
    } catch (error) {
      console.error("Erro ao carregar dados do usuário:", error);
      localStorage.removeItem("token");
    } finally {
      setLoading(false);
    }
  };

  const handleLogin = (userData: {
    id: number;
    name: string;
    email: string;
    token: string;
  }) => {
    const userWithDefaults = {
      ...userData,
      bio: "Apaixonado por conexões genuínas e boas vibes! 🌟",
      location: "São Paulo, Brasil",
      joinDate: "Janeiro 2025",
    };
    setUser(userWithDefaults);
    localStorage.setItem("token", userData.token);
  };

  const handleLogout = () => {
    notificationService.disconnect();
    localStorage.removeItem("token");
    setUser(null);
    setRealtimeNotifications([]);
  };

  const clearRealtimeNotifications = () => {
    setRealtimeNotifications([]);
  };

  // Generate profile URL for current user
  const generateMyProfileUrl = () => {
    if (user?.id && (user as any).username) {
      const paddedId = user.id.toString().padStart(10, "0");
      const username = (user as any).username;
      return `/@${username}/id/${paddedId}`;
    }
    return "/profile";
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (!user) {
    return <EnhancedAuth onLogin={handleLogin} />;
  }

  return (
    <Router>
      <Layout user={user} onLogout={handleLogout}>
        <Routes>
          {/* Home Feed */}
          <Route path="/" element={<Feed user={user} />} />

          {/* Current User Profile */}
          <Route path="/profile" element={<Profile user={user} />} />

          {/* Chat Page */}
          <Route path="/chat" element={<ChatPage user={user} />} />

          {/* User Profile with @username/id/### format */}
          <Route
            path="/@:username/id/:id"
            element={<ProfileRoute currentUser={user} />}
          />

          {/* Legacy profile routes - redirect to new format */}
          <Route
            path="/user/:id"
            element={<Navigate to={generateMyProfileUrl()} replace />}
          />

          {/* Catch all - redirect to home */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </Layout>
    </Router>
  );
}

export default EnhancedApp;
