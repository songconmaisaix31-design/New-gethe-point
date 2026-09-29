import assert from 'node:assert/strict';
import test from 'node:test';
import { createA3RobotAdapter } from '../src/adapter.ts';
import { createAiGateway } from '../src/ai-gateway.ts';
import { createMockA3Client } from '../src/mock-client.ts';
import type { A3Client } from '../src/a3-client.ts';

test('executes an allowlisted speak command in mock mode', async () => {
  const execute = createAiGateway(createA3RobotAdapter({ client: createMockA3Client(), mode: 'mock', enabled: false }));
  const result = await execute({
    action: 'speak',
    template: 'care_reminder',
    data: { title: 'Medicine', instruction: 'Take it after the meal' },
    priority: 'normal',
  });
  assert.equal(result.ok, true);
  if (result.ok && result.action === 'speak') assert.equal(result.terminalStatus, 'TTSStatusType_NOTInQue');
});

test('rejects unknown actions and extra fields', async () => {
  const execute = createAiGateway(createA3RobotAdapter({ client: createMockA3Client(), mode: 'mock', enabled: false }));
  assert.deepEqual(await execute({ action: 'move', joint: 'neck' }), { ok: false, error: 'INVALID_COMMAND' });
  assert.deepEqual(await execute({ action: 'status', traceId: 'trace-1', url: 'http://attacker.test' }), { ok: false, error: 'INVALID_COMMAND' });
});

test('rejects oversized rendered text', async () => {
  const execute = createAiGateway(createA3RobotAdapter({ client: createMockA3Client(), mode: 'mock', enabled: false }));
  const result = await execute({
    action: 'speak',
    template: 'care_reminder',
    data: { title: '药'.repeat(400), instruction: 'now' },
    priority: 'normal',
  });
  assert.deepEqual(result, { ok: false, error: 'TTS_TEXT_TOO_LONG' });
});

test('serializes concurrent announcements', async () => {
  const started: string[] = [];
  const releases: Array<() => void> = [];
  const client: A3Client = {
    play: async () => ({ traceId: 'unused', remoteTraceId: 'unused' }),
    getStatus: async () => 'TTSStatusType_NOTInQue',
    stop: async () => undefined,
    playAndWait: async (text) => {
      started.push(text);
      await new Promise<void>((resolve) => releases.push(resolve));
      return {
        traceId: `trace-${started.length}`,
        remoteTraceId: `remote-${started.length}`,
        terminalStatus: 'TTSStatusType_NOTInQue',
      };
    },
  };
  const adapter = createA3RobotAdapter({ client, mode: 'mock', enabled: false });
  const first = adapter.speak('care_reminder', { title: 'A', instruction: 'one' }, 'normal');
  const second = adapter.speak('care_reminder', { title: 'B', instruction: 'two' }, 'normal');
  await new Promise<void>((resolve) => setImmediate(resolve));
  assert.equal(started.length, 1);
  releases.shift()?.();
  await first;
  await new Promise<void>((resolve) => setImmediate(resolve));
  assert.equal(started.length, 2);
  releases.shift()?.();
  await second;
});

test('requires explicit enablement in real mode', async () => {
  const execute = createAiGateway(createA3RobotAdapter({ client: createMockA3Client(), mode: 'real', enabled: false }));
  const result = await execute({
    action: 'speak',
    template: 'handover_confirm',
    data: { domainName: 'Medicine' },
    priority: 'normal',
  });
  assert.deepEqual(result, { ok: false, error: 'ROBOT_DISABLED' });
});
