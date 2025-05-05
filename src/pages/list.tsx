import { useEffect, useState, useTransition } from "react";
import { useRouter } from "next/navigation";
import {
  Box,
  Button,
  CircularProgress,
  FormControlLabel,
  Grid2 as Grid,
  Switch,
  Typography,
} from "@mui/material";
import { GoogleLogin } from "@react-oauth/google";
import { useAuth } from "@/lib/useAuth";
import { hiraToKata } from "@/lib/util";
import { API_URL } from "@/config/config";

export default function Home() {
  const auth = useAuth();
  const router = useRouter();
  const [words, setWords] = useState<string[]>([]);
  const [katakana, setKatakana] = useState(false);
  const [isPending, startTransition] = useTransition();

  const fetchWordList = async () => {
    if (!auth.isAuthenticated) return;
    try {
      const res = await fetch(`${API_URL}/favorites`, {
        headers: { Authorization: `Bearer ${auth.credential}` },
      });
      const words: string[] = await res.json();
      setWords(words);
    } catch (e: any) {
      console.error(e);
    }
  };

  useEffect(() => {
    startTransition(fetchWordList);
  }, [auth.isAuthenticated]);

  return (
    <Box>
      <Grid container spacing={5} sx={{ p: 5, pb: 10, minWidth: 800 }}>
        <Grid size={12}>
          <Typography variant="h4" sx={{ textAlign: "center" }}>
            単語リスト
          </Typography>
        </Grid>
        
        {!auth.isAuthenticated ? (
          <Box>
            <GoogleLogin onSuccess={auth.googleLogin} />
          </Box>
        ) : isPending ? (
          <Box sx={{ display: "flex", gap: 1, alignItems: "center" }}>
            Loading...
            <CircularProgress size={20} />
          </Box>
        ) : (
          <>
            <Grid size={12}>
              <FormControlLabel
                label="片仮名"
                control={<Switch checked={katakana} onChange={() => setKatakana((prev) => !prev)} />}
              />
            </Grid>
            <Grid container spacing={1} size={12}>
              {words.map((word, i) => (
                <Grid size={{ xs: 4, sm: 3, lg: 2 }} key={i}>
                  <Typography variant="body1">
                    {katakana ? hiraToKata(word) : word}
                  </Typography>
                </Grid>
              ))}
            </Grid>
          </>
        )}
        <Grid size={12}>
          <Button
            size="medium"
            color="primary"
            variant="text"
            onClick={() => startTransition(() => router.push("/"))}
          >
            ⇒戻る
          </Button>
        </Grid>
      </Grid>
    </Box>
  );
}