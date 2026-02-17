import { 
  Home, 
  MessageSquare, 
  BookOpen, 
  LayoutDashboard, 
  BarChart3, 
  Settings, 
  Moon, 
  Sun,
  Shield,
  Zap,
  LogIn,
  LogOut,
  User
} from "lucide-react";
import { NavLink, useLocation, useNavigate } from "react-router-dom";
import { cn } from "@/lib/utils";
import { useTheme } from "@/contexts/ThemeContext";
import { useAuth } from "@/contexts/AuthContext";
import {
  Sidebar,
  SidebarContent,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarHeader,
  SidebarFooter,
  useSidebar,
} from "@/components/ui/sidebar";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

const mainNavItems = [
  { title: "Home", url: "/", icon: Home },
  { title: "Chat", url: "/chat", icon: MessageSquare },
  { title: "Training", url: "/training", icon: BookOpen },
  { title: "Dashboard", url: "/dashboard", icon: LayoutDashboard },
  { title: "Analytics", url: "/analytics", icon: BarChart3 },
];

const settingsItems = [
  { title: "Settings", url: "/settings", icon: Settings },
];

export function AppSidebar() {
  const { state } = useSidebar();
  const collapsed = state === "collapsed";
  const location = useLocation();
  const navigate = useNavigate();
  const { theme, toggleMode } = useTheme();
  const { user, isAuthenticated, logout } = useAuth();

  const isActive = (path: string) => {
    if (path === "/") return location.pathname === "/";
    return location.pathname.startsWith(path);
  };

  const handleLogout = () => {
    logout();
    navigate("/");
  };

  // Tutorial target IDs for specific nav items
  const tutorialTargets: Record<string, string> = {
    "/dashboard": "dashboard-link",
    "/chat": "chat-link",
    "/training": "training-link",
  };

  return (
    <Sidebar 
      className={cn(
        "border-r border-border/50 transition-all duration-300",
        "bg-sidebar/80 backdrop-blur-xl"
      )}
      collapsible="icon"
      data-tutorial="sidebar"
    >
      <SidebarHeader className="p-4 border-b border-border/30">
        <div className={cn(
          "flex items-center gap-3 transition-all duration-300",
          collapsed && "justify-center"
        )}>
          <div className="relative">
            <Shield className="h-8 w-8 text-primary animate-pulse-glow" />
            <Zap className="h-4 w-4 text-secondary absolute -bottom-1 -right-1" />
          </div>
          {!collapsed && (
            <div className="flex flex-col">
              <span className="font-cyber font-bold text-lg text-primary neon-text-cyan">
                CYBER
              </span>
              <span className="font-cyber text-xs text-secondary -mt-1">
                SENSEI
              </span>
            </div>
          )}
        </div>
      </SidebarHeader>

      <SidebarContent className="px-2">
        <SidebarGroup>
          <SidebarGroupLabel className={cn(
            "text-muted-foreground/60 uppercase tracking-wider text-xs",
            collapsed && "sr-only"
          )}>
            Navigation
          </SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              {mainNavItems.map((item) => (
                <SidebarMenuItem key={item.title}>
                  <SidebarMenuButton asChild>
                    <NavLink
                      to={item.url}
                      data-tutorial={tutorialTargets[item.url]}
                      className={cn(
                        "flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all duration-200",
                        "hover:bg-primary/10 hover:text-primary",
                        "group relative overflow-hidden",
                        isActive(item.url) && "bg-primary/15 text-primary neon-border"
                      )}
                    >
                      <item.icon className={cn(
                        "h-5 w-5 transition-all duration-200",
                        "group-hover:scale-110",
                        isActive(item.url) && "text-primary drop-shadow-[0_0_8px_hsl(var(--primary))]"
                      )} />
                      {!collapsed && (
                        <span className="font-medium">{item.title}</span>
                      )}
                      {isActive(item.url) && (
                        <div className="absolute left-0 top-0 bottom-0 w-1 bg-primary rounded-r" />
                      )}
                    </NavLink>
                  </SidebarMenuButton>
                </SidebarMenuItem>
              ))}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>

        <SidebarGroup className="mt-auto">
          <SidebarGroupLabel className={cn(
            "text-muted-foreground/60 uppercase tracking-wider text-xs",
            collapsed && "sr-only"
          )}>
            System
          </SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              {settingsItems.map((item) => (
                <SidebarMenuItem key={item.title}>
                  <SidebarMenuButton asChild>
                    <NavLink
                      to={item.url}
                      className={cn(
                        "flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all duration-200",
                        "hover:bg-primary/10 hover:text-primary",
                        "group",
                        isActive(item.url) && "bg-primary/15 text-primary neon-border"
                      )}
                    >
                      <item.icon className={cn(
                        "h-5 w-5 transition-all duration-200",
                        "group-hover:scale-110"
                      )} />
                      {!collapsed && (
                        <span className="font-medium">{item.title}</span>
                      )}
                    </NavLink>
                  </SidebarMenuButton>
                </SidebarMenuItem>
              ))}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>

      <SidebarFooter className="p-4 border-t border-border/30 space-y-2">
        {/* User/Auth Section */}
        {isAuthenticated && user ? (
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button
                variant="ghost"
                size={collapsed ? "icon" : "default"}
                className={cn(
                  "w-full justify-start gap-2 hover:bg-primary/10",
                  collapsed && "justify-center"
                )}
              >
                <div className="w-7 h-7 rounded-full bg-primary/20 flex items-center justify-center text-lg">
                  {user.avatar}
                </div>
                {!collapsed && (
                  <span className="truncate text-sm">{user.name}</span>
                )}
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent 
              align="end" 
              className="w-56 bg-card border-border/50"
            >
              <div className="px-2 py-1.5">
                <p className="text-sm font-medium">{user.name}</p>
                <p className="text-xs text-muted-foreground truncate">{user.email}</p>
              </div>
              <DropdownMenuSeparator />
              <DropdownMenuItem onClick={() => navigate("/settings")}>
                <User className="h-4 w-4 mr-2" />
                Profile Settings
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem onClick={handleLogout} className="text-destructive">
                <LogOut className="h-4 w-4 mr-2" />
                Logout
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        ) : (
          <Button
            variant="ghost"
            size={collapsed ? "icon" : "default"}
            onClick={() => navigate("/auth")}
            className={cn(
              "w-full justify-center gap-2 hover:bg-primary/10",
              "transition-all duration-200"
            )}
          >
            <LogIn className="h-5 w-5 text-primary" />
            {!collapsed && <span>Login</span>}
          </Button>
        )}

        {/* Theme Toggle */}
        <Button
          variant="ghost"
          size={collapsed ? "icon" : "default"}
          onClick={toggleMode}
          className={cn(
            "w-full justify-center gap-2 hover:bg-primary/10",
            "transition-all duration-200"
          )}
        >
          {theme.mode === 'dark' ? (
            <>
              <Sun className="h-5 w-5 text-neon-orange" />
              {!collapsed && <span>Light Mode</span>}
            </>
          ) : (
            <>
              <Moon className="h-5 w-5 text-neon-purple" />
              {!collapsed && <span>Dark Mode</span>}
            </>
          )}
        </Button>
      </SidebarFooter>
    </Sidebar>
  );
}
