// Vercel Serverless Function：counterapi.dev v2 的安全中繼
// 目的：API 金鑰只存在 Vercel 環境變數（伺服器端），不會出現在前端原始碼裡。
//
// 用法：
//   /api/count?key=pageview&action=up   → 計數 +1
//   /api/count?key=pageview&action=get  → 讀目前數字（預設值，action 省略也是 get）
//   可選加 &ns=your-workspace 覆蓋預設 workspace（不填就用環境變數或內建預設值）
//
// 需要在 Vercel 專案設定 → Environment Variables 新增：
//   COUNTERAPI_KEY       = 你在 counterapi.dev 產生的 API Key
//   COUNTERAPI_WORKSPACE = 你的 workspace 名稱（例如 nina1minaday，選填，沒設就用內建預設值）

const DEFAULT_WORKSPACE = 'nina1minaday';
const KEY_PATTERN = /^[a-zA-Z0-9_-]{1,80}$/;
const NS_PATTERN = /^[a-zA-Z0-9_-]{1,60}$/;

module.exports = async function handler(req, res) {
  res.setHeader('Cache-Control', 'no-store');

  const key = String(req.query.key || '');
  const action = String(req.query.action || 'get');
  const ns = String(req.query.ns || process.env.COUNTERAPI_WORKSPACE || DEFAULT_WORKSPACE);

  if (!KEY_PATTERN.test(key)) return res.status(400).json({ error: 'invalid key' });
  if (!NS_PATTERN.test(ns)) return res.status(400).json({ error: 'invalid ns' });

  const apiKey = process.env.COUNTERAPI_KEY;
  if (!apiKey) return res.status(200).json({ count: 0, configured: false });

  const suffix = action === 'up' ? '/up' : '';
  const upstreamUrl = `https://api.counterapi.dev/v2/${encodeURIComponent(ns)}/${encodeURIComponent(key)}${suffix}`;

  try {
    const upstream = await fetch(upstreamUrl, {
      headers: { Authorization: `Bearer ${apiKey}` }
    });
    const data = await upstream.json().catch(() => null);
    const count = data && data.data ? (data.data.up_count || 0) : 0;
    const debugInfo = req.query.debug
      ? { upstreamStatus: upstream.status, upstreamBody: data, ns, keyLen: apiKey.length }
      : undefined;
    return res.status(200).json({ count, configured: true, ...(debugInfo ? { debug: debugInfo } : {}) });
  } catch (e) {
    return res.status(200).json({ count: 0, configured: true, error: 'upstream_failed', message: String(e) });
  }
}
