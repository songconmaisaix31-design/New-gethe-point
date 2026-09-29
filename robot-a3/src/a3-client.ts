import { randomUUID } from 'node:crypto';
import { RobotError, type AudioStatus, type Priority } from './contracts.ts';

const paths = {
  play: '/rpc/aimdk.protocol.TTSService/PlayTTS',
  status: '/rpc/aimdk.protocol.TTSService/GetAudioStatus',
  stop: '/rpc/aimdk.protocol.TTSService/StopTTSTraceId',
} as const;

const knownStatuses = new Set<AudioStatus>([
  'TTSConfigStatusType_Unknown',
  'TTSStatusType_Begin',
  'TTSStatusType_Playing',
  'TTSStatusType_End',
  'TTSStatusType_Stop',
  'TTSStatusType_Error',
  'TTSStatusType_InQue',
  'TTSStatusType_NOTInQue',
]);

export type A3ClientOptions = {
  baseUrl: string;
  domain: string;
  requestTimeoutMs: number;
  playbackTimeoutMs: number;
  pollIntervalMs: number;
  fetchImpl?: typeof fetch;
  sleep?: (milliseconds: number) => Promise<void>;
  createTraceId?: () => string;
};

type JsonRecord = Record<string, unknown>;

function asRecord(value: unknown): JsonRecord {
  if (typeof value !== 'object' || value === null || Array.isArray(value)) {
    throw new RobotError('ROBOT_PROTOCOL_ERROR');
  }
  return value as JsonRecord;
}

function asAudioStatus(value: unknown): AudioStatus {
  if (typeof value !== 'string' || !knownStatuses.has(value as AudioStatus)) {
    throw new RobotError('ROBOT_PROTOCOL_ERROR');
  }
  return value as AudioStatus;
}

function priorityToInterruption(priority: Priority): boolean {
  return priority !== 'normal';
}

export function createA3Client(options: A3ClientOptions) {
  const fetchImpl = options.fetchImpl ?? fetch;
  const sleep = options.sleep ?? ((milliseconds) => new Promise<void>((resolve) => setTimeout(resolve, milliseconds)));
  const createTraceId = options.createTraceId ?? (() => `gethepoint-${randomUUID()}`);

  async function post(path: string, body: JsonRecord): Promise<JsonRecord> {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), options.requestTimeoutMs);
    try {
      const response = await fetchImpl(`${options.baseUrl}${path}`, {
        method: 'POST',
        headers: { 'content-type': 'application/json' },
        body: JSON.stringify(body),
        signal: controller.signal,
      });
      if (!response.ok) throw new RobotError('ROBOT_PROTOCOL_ERROR');
      return asRecord(await response.json());
    } catch (error) {
      if (error instanceof RobotError) throw error;
      throw new RobotError('ROBOT_UNREACHABLE');
    } finally {
      clearTimeout(timeout);
    }
  }

  async function play(text: string, priority: Priority) {
    const traceId = createTraceId();
    const response = await post(paths.play, {
      text,
      priority_level: 'INTERACTION_L6',
      domain: options.domain,
      trace_id: traceId,
      is_interrupted: priorityToInterruption(priority),
    });
    const remoteTraceId = response.trace_id;
    if (typeof remoteTraceId !== 'string' || remoteTraceId.length === 0) {
      throw new RobotError('ROBOT_PROTOCOL_ERROR');
    }
    const accepted = response.is_success ?? response.is_sucess;
    if (accepted === false) throw new RobotError('PLAYBACK_ERROR');
    return { traceId, remoteTraceId };
  }

  async function getStatus(traceId: string): Promise<AudioStatus> {
    const response = await post(paths.status, { trace_id: traceId });
    const statusRecord = asRecord(response.tts_status);
    return asAudioStatus(statusRecord.tts_status);
  }

  async function stop(traceId: string): Promise<void> {
    await post(paths.stop, { trace_id: traceId });
  }

  async function playAndWait(text: string, priority: Priority) {
    const started = await play(text, priority);
    const deadline = Date.now() + options.playbackTimeoutMs;
    while (Date.now() < deadline) {
      const status = await getStatus(started.traceId);
      if (status === 'TTSStatusType_End' || status === 'TTSStatusType_NOTInQue') {
        return { ...started, terminalStatus: status };
      }
      if (status === 'TTSStatusType_Error' || status === 'TTSStatusType_Stop') {
        throw new RobotError('PLAYBACK_ERROR');
      }
      await sleep(options.pollIntervalMs);
    }
    throw new RobotError('PLAYBACK_TIMEOUT');
  }

  return { play, getStatus, stop, playAndWait };
}

export type A3Client = ReturnType<typeof createA3Client>;
