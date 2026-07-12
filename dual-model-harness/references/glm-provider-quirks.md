# GLM 5.2 / Z.AI Provider — Quirks & Fixes

## Thinking Mode Default (FIXED 2026-07-11)

GLM 5.2 defaults to thinking mode ON when the `thinking` field is omitted from
the request body. This burns the token budget on internal reasoning before
producing any output — 50 reasoning tokens for "hello", empty content.

### Root Cause

The Z.AI Hermes provider at `plugins/model-providers/zai/__init__.py` only
emitted the `thinking` field when `reasoning_config` was explicitly set.

### Fix

Patched lines 94-101. Changed from:

```python
# OLD — only emit when reasoning_config is set
if isinstance(reasoning_config, dict):
    enabled = reasoning_config.get("enabled") is not False
    extra_body["thinking"] = {"type": "enabled" if enabled else "disabled"}
```

To:

```python
# NEW — always emit, default DISABLED
if _model_supports_thinking(model) or _is_glm_5_2(model):
    if isinstance(reasoning_config, dict) and reasoning_config.get("enabled") is True:
        extra_body["thinking"] = {"type": "enabled"}
    else:
        extra_body["thinking"] = {"type": "disabled"}
```

After patching, restart the gateway:
```bash
systemctl --user kill hermes-gateway -s SIGKILL && sleep 2 && systemctl --user start hermes-gateway
```

### Before/After

| Scenario | Before | After |
|----------|--------|-------|
| `"Say hello"` response | ~35s (all thinking) | ~2s (no thinking) |
| `"Say hello"` tokens | 50 reasoning, 0 content | 0 reasoning, 12 content |
| 16-file read delegation | 600s timeout | untested |
| Multi-turn coding task | 41s per turn | ~2s per turn |

### How to Enable Thinking

Set in config.yaml or via `/reasoning high` in session:
```yaml
reasoning_effort: high  # or max
```
The provider then sends `"thinking":{"type":"enabled"}` + `"reasoning_effort":"high"`.

## API Endpoint

- Base URL: `https://api.z.ai/api/paas/v4`
- Auth: Bearer token from env var `ZAI_API_KEY` (alias: `GLM_API_KEY`, `Z_AI_API_KEY`)
- Model names: `glm-5.2` (primary), `glm-5`, `glm-4-9b`
- Fallback models: `glm-4.5-flash` as default aux model

## Diagnostic

```bash
curl -s --max-time 15 https://api.z.ai/api/paas/v4/chat/completions \
  -H "Authorization: Bearer $ZAI_API_KEY" \
  -d '{"model":"glm-5.2","messages":[{"role":"user","content":"say hello"}],
       "max_tokens":50,"thinking":{"type":"disabled"}}'
```
