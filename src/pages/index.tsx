import { useEffect, useState, useTransition } from "react";
import { useRouter } from "next/navigation";
import {
  Box,
  Button,
  CircularProgress,
  FormControlLabel,
  Grid2 as Grid,
  IconButton,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Switch,
  Typography,
} from "@mui/material";
import {
  AddCircle,
  AddCircleOutline,
  Circle,
  CircleOutlined,
  RemoveCircle,
  RemoveCircleOutline,
  Star,
  StarOutline,
} from "@mui/icons-material";
import { GoogleLogin } from "@react-oauth/google";
import { useAuth } from "@/lib/useAuth";
import { hiraToKata } from "@/lib/util";
import { API_URL } from "@/config/config";

export default function Home() {
  const auth = useAuth();

  const description = `ランダムに生成された文字列から良い感じの部分を取り出して単語を作ること
  「つぃみぐの」は機械学習を利用して効率的にペユドチできるようにしたツールです。`;

  const peyudochiSamples = [
    "https://www.youtube.com/embed/h3AyHy71MHs",
    "https://www.youtube.com/embed/4UFr8N6TF5s",
  ];

  return (
    <Box>
      <Grid container spacing={5} sx={{ p: 5, pb: 10, minWidth: 800 }}>
        <Grid size={12}>
          <Typography variant="h4" sx={{ textAlign: "center" }}>
            つぃみぐの（ペユドチ支援ツール）
          </Typography>
        </Grid>

        <Grid size={12}>
          <Typography variant="h5" sx={{ mb: 1 }}>
            ペユドチとは
          </Typography>
          {description.split("\n").map((line, i) => (
            <Typography variant="body2" key={i}>
              {line}
            </Typography>
          ))}
        </Grid>

        <Grid container spacing={3} size={12}>
          <Grid size={12}>
            <Typography variant="h5">
              活用例
            </Typography>
          </Grid>
          {peyudochiSamples.map((url) => (
            <Grid key={url} size={{ xs: 6, lg: 4 }}>
              <iframe
                src={url}
                width={352}
                height={198}
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture;"
                allowFullScreen
                style={{ border: "none" }}
              />
            </Grid>
          ))}
        </Grid>

        <Grid container spacing={2} size={12}>
          <Grid size={12}>
            <Typography variant="h5">
              Let&#39;s ペユドチ
            </Typography>
            <List dense>
              <ListItem>
                <ListItemIcon>
                  <Star color="warning" />
                </ListItemIcon>
                <ListItemText primary="気に入った単語（リストに追加）" />
              </ListItem>
              <ListItem>
                <ListItemIcon>
                  <AddCircle color="success" />
                </ListItemIcon>
                <ListItemText primary="気に入った単語（リストに追加しない）" />
              </ListItem>
              <ListItem>
                <ListItemIcon>
                  <RemoveCircle color="error" />
                </ListItemIcon>
                <ListItemText primary="気に入らない単語" />
              </ListItem>
            </List>
            <Typography variant="body2">
              評価を入力して送信していくとだんだん好みの単語が出やすくなっていきます
            </Typography>
          </Grid>
          {auth.isAuthenticated ? (
            <Box>
              <WordSelector />
            </Box>
          ) : (
            <GoogleLogin onSuccess={auth.googleLogin} />
          )}
        </Grid>
      </Grid>
    </Box>
  );
}

type Candidate = {
  word: string;
  score: number;
};

const WordSelector = () => {
  const auth = useAuth();
  const router = useRouter();
  const [candidates, setCandidates] = useState<Candidate[]>([]);
  const [katakana, setKatakana] = useState(false);
  const [changed, setChanged] = useState(false);
  const [isPending, startTransition] = useTransition();

  const fetchCandidates = async () => {
    if (!auth.isAuthenticated) return;
    try {
      const res = await fetch(`${API_URL}/candidates`, {
        headers: { Authorization: `Bearer ${auth.credential}` },
      });
      const words: string[] = await res.json();
      setCandidates(words.map((w) => ({ word: w, score: 0 })));
    } catch (e: any) {
      console.error(e);
    }
    setChanged(false);
  };

  const sendEval = async () => {
    if (!auth.isAuthenticated) return;
    try {
      const postData = candidates.reduce((acc, c) => ({ ...acc, [c.word]: c.score }), {});
      const res = await fetch(`${API_URL}/eval`, {
        method: "POST",
        headers: { Authorization: `Bearer ${auth.credential}`, "Content-Type": "application/json" },
        body: JSON.stringify(postData),
      });
      const words: string[] = await res.json();
      setCandidates(words.map((w) => ({ word: w, score: 0 })));
    } catch (e: any) {
      console.error(e);
    }
    setChanged(false);
  };

  const onClickEval = (word: string, score: number) => {
    setCandidates((prev) => prev.map((c) => c.word == word ? { ...c, score } : c));
    setChanged(true);
  };

  useEffect(() => {
    startTransition(fetchCandidates);
  }, [auth.isAuthenticated]);

  return (
    <>
      {candidates.length == 0 ? (
        <Box sx={{ display: "flex", gap: 1, alignItems: "center" }}>
          Loading...
          <CircularProgress size={20} />
        </Box>
      ) : (
        <>
          <Box>
            <FormControlLabel
              label="片仮名"
              control={<Switch checked={katakana} onChange={() => setKatakana((prev) => !prev)} />}
            />
            <List dense sx={{ width: 320 }}>
              {candidates.map((c, i) => (
                <ListItem
                  key={`words_${i}`}
                  secondaryAction={
                    <Box sx={{ display: "flex", gap: 0.3 }}>
                      <IconButton edge="end" color="warning" disabled={isPending} onClick={() => onClickEval(c.word, 1)}>
                        {c.score == 1 ? <Star /> : <StarOutline />}
                      </IconButton>
                      <IconButton edge="end" color="success" disabled={isPending} onClick={() => onClickEval(c.word, 0.7)}>
                        {c.score == 0.7 ? <AddCircle /> : <AddCircleOutline />}
                      </IconButton>
                      <IconButton edge="end" disabled={isPending} onClick={() => onClickEval(c.word, 0)}>
                        {c.score == 0 ? <Circle /> : <CircleOutlined />}
                      </IconButton>
                      <IconButton edge="end" color="error" disabled={isPending} onClick={() => onClickEval(c.word, -0.7)}>
                        {c.score == -0.7 ? <RemoveCircle /> : <RemoveCircleOutline />}
                      </IconButton>
                    </Box>
                  }
                >
                  <ListItemText primary={katakana ? hiraToKata(c.word) : c.word} />
                </ListItem>
              ))}
            </List>
          </Box>
          <Box sx={{ display: "flex", gap: 1, alignItems: "center" }}>
            <Button
              size="large"
              color="primary"
              variant="contained"
              disabled={isPending || !changed}
              onClick={() => startTransition(sendEval)}
            >
              送信
            </Button>
            {candidates.length > 0 && isPending && (
              <CircularProgress size={30} />
            )}
          </Box>
          <Button
            size="medium"
            color="primary"
            variant="text"
            onClick={() => startTransition(() => router.push("/list"))}
            sx={{ mt: 2 }}
          >
            ⇒選んだ単語リスト
          </Button>
        </>
      )}
    </>
  );
};