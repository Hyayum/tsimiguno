import type { AppProps } from "next/app";
import { useRouter } from "next/router";
import Head from "next/head";
import { useState, useTransition } from "react";
import {
  createTheme,
  ThemeProvider,
  Backdrop,
  Box,
  CircularProgress,
  Divider,
  Drawer,
  IconButton,
  List,
  ListItemText,
} from "@mui/material";
import { ChevronLeft, Menu } from "@mui/icons-material";
import { GoogleLogin, GoogleOAuthProvider } from "@react-oauth/google";
import { GOOGLE_CLIENT_ID } from "@/config/config";
import { AuthProvider, useAuth } from "@/lib/useAuth";

const theme = createTheme({
  typography: {
    button: {
      textTransform: "none",
    },
    h5: {
      "&::before": {
        content: '""',
        backgroundColor: "#d6a2f8",
        position: "relative",
        top: 21,
        left: -18,
        width: 12,
        height: 12,
        display: "block",
        transform: "rotate(45deg)",
      },
    },
    h6: {
      "::before": {
        content: '""',
        backgroundColor: "#84aaf8",
        position: "relative",
        top: 21,
        left: -18,
        width: 10,
        height: 10,
        borderRadius: 5,
        display: "block",
      },
    },
  },
  components: {
    MuiCheckbox: {
      styleOverrides: {
        root: {
          padding: 4,
        },
      },
    },
    MuiTextField: {
      styleOverrides: {
        root: {
          backgroundColor: "#fff",
        },
      },
    },
    MuiListItemIcon: {
      styleOverrides: {
        root: {
          minWidth: 35,
        },
      },
    },
  },
});

const menuLinks = [
  { name: "TOP", path: "/", desc: "" },
  { name: "単語リスト", path: "/list", desc: "今までリストに追加してきた単語一覧" },
];

const Layout = ({ children }: { children: React.ReactNode }) => {
  const router = useRouter();
  const auth = useAuth();
  const [isPending, startTransition] = useTransition();
  const [drawerOpen, setDrawerOpen] = useState(false);

  const handleClickLink = (path: string) => {
    setDrawerOpen(false);
    startTransition(() => {
      router.push(path);
    });
  };

  return (
    <Box>
      <IconButton
        size="large"
        sx={{ position: "fixed", top: 10, left: 10, bgcolor: "#bbb5", zIndex: 1000 }}
        onClick={(e) => setDrawerOpen(true)}
      >
        <Menu />
      </IconButton>
      <Drawer open={drawerOpen} onClose={() => setDrawerOpen(false)} PaperProps={{ sx: { maxWidth: 300 } }}>
        <Box sx={{ p: 1, display: "flex", justifyContent: "right" }}>
          <IconButton onClick={() => setDrawerOpen(false)}>
            <ChevronLeft />
          </IconButton>
        </Box>
        <List>
          {menuLinks.map((link) => (
            <ListItemText
              primary={link.name}
              secondary={link.desc}
              slotProps={{ secondary: { fontSize: 12, color: "#999" } }}
              key={link.path}
              onClick={() => handleClickLink(link.path)}
              sx={{
                cursor: "pointer",
                m: 0,
                px: 2,
                py: 1,
                bgcolor: router.pathname == link.path ? "#f0f0f0" : "#fff",
                "&:hover": { bgcolor: "#e0e0e0" },
              }}
            />
          ))}
        </List>
        <Divider />
        <List>
          {auth.isAuthenticated ? (
            <ListItemText
              primary="ログアウト"
              slotProps={{ secondary: { fontSize: 12, color: "#999" } }}
              onClick={auth.logout}
              sx={{
                cursor: "pointer",
                m: 0,
                px: 2,
                py: 1,
                "&:hover": { bgcolor: "#e0e0e0" },
              }}
            />
          ) : (
            <GoogleLogin onSuccess={auth.googleLogin} />
          )}
        </List>
      </Drawer>
      <Box>
        {children}
      </Box>
      <Backdrop open={isPending}>
        <CircularProgress sx={{ color: "white" }} />
      </Backdrop>
    </Box>
  );
};

export default function App({ Component, pageProps }: AppProps) {
  return (
    <GoogleOAuthProvider clientId={GOOGLE_CLIENT_ID}>
      <AuthProvider>
        <ThemeProvider theme={theme}>
          <Head>
            <title>つぃみぐの / ペユドチ支援ツール</title>
            <link rel="icon" href="/tsimiguno/favicon.ico" />
          </Head>
          <Layout>
            <Component {...pageProps} />
          </Layout>
        </ThemeProvider>
      </AuthProvider>
    </GoogleOAuthProvider>
  );
}
