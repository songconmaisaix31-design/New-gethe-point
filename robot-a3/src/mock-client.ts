import type { A3Client } from './a3-client.ts';
import type { AudioStatus, Priority } from './contracts.ts';

export function createMockA3Client(): A3Client {
  let counter = 0;
  const states = new Map<string, AudioStatus>();

  async function play(_text: string, _priority: Priority) {
    const traceId = `mock-${++counter}`;
    states.set(traceId, 'TTSStatusType_Playing');
    return { traceId, remoteTraceId: traceId };
  }

  async function getStatus(traceId: string): Promise<AudioStatus> {
    const current = states.get(traceId) ?? 'TTSStatusType_NOTInQue';
    if (current === 'TTSStatusType_Playing') states.set(traceId, 'TTSStatusType_NOTInQue');
    return current;
  }

  async function stop(traceId: string): Promise<void> {
    states.set(traceId, 'TTSStatusType_Stop');
  }

  async function playAndWait(text: string, priority: Priority) {
    const started = await play(text, priority);
    await getStatus(started.traceId);
    const terminalStatus = 'TTSStatusType_NOTInQue' as const;
    return { ...started, terminalStatus };
  }

  return { play, getStatus, stop, playAndWait };
}
