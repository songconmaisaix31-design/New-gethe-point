import assert from 'node:assert/strict';
import test from 'node:test';
import { createA3Client } from '../src/a3-client.ts';
import { RobotError } from '../src/contracts.ts';

function jsonResponse(value: unknown, status = 200): Response {
  return new Response(JSON.stringify(value), { status, headers: { 'content-type': 'application/json' } });
}

test('uses the official RPC path and request shape', async () => {
  const calls: Array<{ url: string; body: Record<string, unknown> }> = [];
  const client = createA3Client({
    baseUrl: 'http://robot.test:59301',
    domain: 'test-domain',
    requestTimeoutMs: 100,
    playbackTimeoutMs: 100,
    pollIntervalMs: 1,
    createTraceId: () => 'trace-1',
    fetchImpl: async (input, init) => {
      calls.push({ url: String(input), body: JSON.parse(String(init?.body)) as Record<string, unknown> });
      return jsonResponse({ trace_id: 'trace-1-remote', is_sucess: true });
    },
  });
  const result = await client.play('Hello', 'normal');
  assert.equal(result.traceId, 'trace-1');
  assert.deepEqual(calls, [{
    url: 'http://robot.test:59301/rpc/aimdk.protocol.TTSService/PlayTTS',
    body: {
      text: 'Hello',
      priority_level: 'INTERACTION_L6',
      domain: 'test-domain',
      trace_id: 'trace-1',
      is_interrupted: false,
    },
  }]);
});

test('reads nested status and accepts NOTInQue as terminal', async () => {
  const responses = [
    { trace_id: 'trace-2-remote', is_success: true },
    { tts_status: { tts_status: 'TTSStatusType_Playing' } },
    { tts_status: { tts_status: 'TTSStatusType_NOTInQue' } },
  ];
  const client = createA3Client({
    baseUrl: 'http://robot.test:59301',
    domain: 'test-domain',
    requestTimeoutMs: 100,
    playbackTimeoutMs: 100,
    pollIntervalMs: 1,
    createTraceId: () => 'trace-2',
    sleep: async () => undefined,
    fetchImpl: async () => jsonResponse(responses.shift()),
  });
  const result = await client.playAndWait('Hello', 'urgent');
  assert.equal(result.terminalStatus, 'TTSStatusType_NOTInQue');
});

test('fails closed on malformed robot responses', async () => {
  const client = createA3Client({
    baseUrl: 'http://robot.test:59301',
    domain: 'test-domain',
    requestTimeoutMs: 100,
    playbackTimeoutMs: 100,
    pollIntervalMs: 1,
    fetchImpl: async () => jsonResponse({ status: 'TTSStatusType_End' }),
  });
  await assert.rejects(client.getStatus('trace-3'), (error: unknown) => error instanceof RobotError && error.code === 'ROBOT_PROTOCOL_ERROR');
});
