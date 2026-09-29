import { createServer, type IncomingMessage, type ServerResponse } from 'node:http';
import { timingSafeEqual } from 'node:crypto';
import { pathToFileURL } from 'node:url';
import { createA3Client } from './a3-client.ts';
import { createA3RobotAdapter } from './adapter.ts';
import { createAiGateway } from './ai-gateway.ts';
import { loadConfig, type RobotConfig } from './config.ts';
import { createMockA3Client } from './mock-client.ts';

const maxBodyBytes = 32 * 1_024;

function writeJson(response: ServerResponse, status: number, body: unknown): void {
  response.writeHead(status, { 'content-type': 'application/json; charset=utf-8' });
  response.end(JSON.stringify(body));
}

function isAuthorized(request: IncomingMessage, token: string | undefined): boolean {
  if (token === undefined) return true;
  const supplied = request.headers.authorization;
  if (supplied === undefined || !supplied.startsWith('Bearer ')) return false;
  const expectedBuffer = Buffer.from(token);
  const suppliedBuffer = Buffer.from(supplied.slice('Bearer '.length));
  return expectedBuffer.length === suppliedBuffer.length && timingSafeEqual(expectedBuffer, suppliedBuffer);
}

async function readJson(request: IncomingMessage): Promise<unknown> {
  const chunks: Buffer[] = [];
  let size = 0;
  for await (const chunk of request) {
    const buffer = Buffer.isBuffer(chunk) ? chunk : Buffer.from(chunk);
    size += buffer.length;
    if (size > maxBodyBytes) throw new Error('BODY_TOO_LARGE');
    chunks.push(buffer);
  }
  return JSON.parse(Buffer.concat(chunks).toString('utf8')) as unknown;
}

export function createRobotServer(config: RobotConfig) {
  const client = config.mode === 'mock'
    ? createMockA3Client()
    : createA3Client({
        baseUrl: config.baseUrl,
        domain: config.domain,
        requestTimeoutMs: config.requestTimeoutMs,
        playbackTimeoutMs: config.playbackTimeoutMs,
        pollIntervalMs: config.pollIntervalMs,
      });
  const adapter = createA3RobotAdapter({ client, mode: config.mode, enabled: config.enabled });
  const execute = createAiGateway(adapter);

  return createServer(async (request, response) => {
    if (!isAuthorized(request, config.gatewayToken)) {
      writeJson(response, 401, { ok: false, error: 'UNAUTHORIZED' });
      return;
    }
    if (request.method === 'GET' && request.url === '/health') {
      writeJson(response, 200, { ok: true, mode: config.mode, robotEnabled: config.mode === 'real' && config.enabled });
      return;
    }
    if (request.method === 'POST' && request.url === '/v1/robot/commands') {
      try {
        const result = await execute(await readJson(request));
        writeJson(response, result.ok ? 200 : 400, result);
      } catch {
        writeJson(response, 400, { ok: false, error: 'INVALID_COMMAND' });
      }
      return;
    }
    writeJson(response, 404, { ok: false, error: 'NOT_FOUND' });
  });
}

if (process.argv[1] !== undefined && import.meta.url === pathToFileURL(process.argv[1]).href) {
  const config = loadConfig();
  const server = createRobotServer(config);
  server.listen(config.gatewayPort, config.gatewayHost, () => {
    process.stdout.write(`A3 robot gateway listening on http://${config.gatewayHost}:${config.gatewayPort} (${config.mode})\n`);
  });
}
