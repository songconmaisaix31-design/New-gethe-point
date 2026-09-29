export type RobotConfig = {
  mode: 'mock' | 'real';
  enabled: boolean;
  baseUrl: string;
  domain: string;
  requestTimeoutMs: number;
  playbackTimeoutMs: number;
  pollIntervalMs: number;
  gatewayHost: string;
  gatewayPort: number;
  gatewayToken?: string;
};

function positiveInteger(value: string | undefined, fallback: number): number {
  if (value === undefined) return fallback;
  const parsed = Number(value);
  if (!Number.isSafeInteger(parsed) || parsed <= 0) {
    throw new Error(`Invalid positive integer configuration: ${value}`);
  }
  return parsed;
}

function normalizeBaseUrl(value: string): string {
  const url = new URL(value);
  if (url.protocol !== 'http:' && url.protocol !== 'https:') {
    throw new Error('ROBOT_BASE_URL must use http or https');
  }
  if (url.username || url.password || url.pathname !== '/' || url.search || url.hash) {
    throw new Error('ROBOT_BASE_URL must contain only scheme, host, and port');
  }
  return url.origin;
}

export function loadConfig(env: NodeJS.ProcessEnv = process.env): RobotConfig {
  const mode = env.ROBOT_MODE ?? 'mock';
  if (mode !== 'mock' && mode !== 'real') {
    throw new Error('ROBOT_MODE must be mock or real');
  }

  const gatewayHost = env.ROBOT_GATEWAY_HOST ?? '127.0.0.1';
  const gatewayToken = env.ROBOT_GATEWAY_TOKEN?.trim() || undefined;
  const loopbackHosts = new Set(['127.0.0.1', '::1', 'localhost']);
  if (!loopbackHosts.has(gatewayHost) && gatewayToken === undefined) {
    throw new Error('ROBOT_GATEWAY_TOKEN is required for non-loopback binding');
  }

  return {
    mode,
    enabled: env.ENABLE_ROBOT === 'true',
    baseUrl: normalizeBaseUrl(env.ROBOT_BASE_URL ?? 'http://10.42.10.10:59301'),
    domain: env.ROBOT_DOMAIN?.trim() || 'gethe-point',
    requestTimeoutMs: positiveInteger(env.ROBOT_REQUEST_TIMEOUT_MS, 5_000),
    playbackTimeoutMs: positiveInteger(env.ROBOT_PLAYBACK_TIMEOUT_MS, 60_000),
    pollIntervalMs: positiveInteger(env.ROBOT_POLL_INTERVAL_MS, 1_000),
    gatewayHost,
    gatewayPort: positiveInteger(env.ROBOT_GATEWAY_PORT, 8_787),
    ...(gatewayToken === undefined ? {} : { gatewayToken }),
  };
}

