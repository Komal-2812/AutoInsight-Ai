import {
  LayoutDashboard,
  Upload,
  FolderOpen,
  MessageSquare,
  BarChart3,
  History,
  Brain,
  LogOut,
  Settings,
} from "lucide-react";
import { NavLink } from "@/components/NavLink";
import { useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "@/hooks/useAuth";
import {
  Sidebar,
  SidebarContent,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarFooter,
  useSidebar,
} from "@/components/ui/sidebar";

const mainItems = [
  { title: "Dashboard", url: "/dashboard", icon: LayoutDashboard },
  { title: "Upload Dataset", url: "/dashboard/upload", icon: Upload },
  { title: "Workspace", url: "/dashboard/workspace", icon: FolderOpen },
  { title: "Chat with AI", url: "/dashboard/chat", icon: MessageSquare },
  { title: "Insights", url: "/dashboard/insights", icon: BarChart3 },
  { title: "History", url: "/dashboard/history", icon: History },
];

export function AppSidebar() {
  const { state } = useSidebar();
  const collapsed = state === "collapsed";
  const location = useLocation();
  const navigate = useNavigate();
  const { signOut } = useAuth();

  const handleLogout = async () => {
    await signOut();
    navigate("/");
  };

  return (
    <Sidebar collapsible="icon">
      <SidebarContent>
        <div className={`flex items-center gap-2 px-4 py-4 ${collapsed ? "justify-center" : ""}`}>
          <div className="h-8 w-8 rounded-lg gradient-bg flex items-center justify-center flex-shrink-0">
            <Brain className="h-4 w-4 text-primary-foreground" />
          </div>
          {!collapsed && <span className="font-bold text-sm">AutoInsight AI</span>}
        </div>

        <SidebarGroup>
          <SidebarGroupLabel>Main</SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              {mainItems.map((item) => (
                <SidebarMenuItem key={item.title}>
                  <SidebarMenuButton asChild>
                    <NavLink to={item.url} end className="hover:bg-sidebar-accent/50" activeClassName="bg-sidebar-accent text-primary font-medium">
                      <item.icon className="h-4 w-4 mr-2" />
                      {!collapsed && <span>{item.title}</span>}
                    </NavLink>
                  </SidebarMenuButton>
                </SidebarMenuItem>
              ))}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>

      <SidebarFooter>
        <SidebarMenu>
          <SidebarMenuItem>
            <SidebarMenuButton onClick={handleLogout} className="hover:bg-sidebar-accent/50 text-muted-foreground cursor-pointer">
              <LogOut className="h-4 w-4 mr-2" />
              {!collapsed && <span>Logout</span>}
            </SidebarMenuButton>
          </SidebarMenuItem>
        </SidebarMenu>
      </SidebarFooter>
    </Sidebar>
  );
}
