import type { A3RobotAdapter } from './adapter.ts';
import {
  RobotError,
  templateNames,
  type GatewayResult,
  type Priority,
  type RobotCommand,
  type TemplateName,
} from './contracts.ts';

const priorities = new Set<Priority>(['normal', 'high', 'urgent']);
const allowedTemplates = new Set<string>(templateNames);
const traceIdPattern = /^[A-Za-z0-9][A-Za-z0-9._:-]{0,199}$/u;

function exactKeys(value: Record<string, unknown>, keys: readonly string[]): boolean {
  const actual = Object.keys(value).sort();
  const expected = [...keys].sort();
  return actual.length === expected.length && actual.every((key, index) => key === expected[index]);
}

function parseCommand(input: unknown): RobotCommand {
  if (typeof input !== 'object' || input === null || Array.isArray(input)) {
    throw new RobotError('INVALID_COMMAND');
  }
  const value = input as Record<string, unknown>;
  if (value.action === 'speak') {
    if (!exactKeys(value, ['action', 'template', 'data', 'priority'])) throw new RobotError('INVALID_COMMAND');
    if (typeof value.template !== 'string' || !allowedTemplates.has(value.template)) throw new RobotError('INVALID_COMMAND');
    if (typeof value.priority !== 'string' || !priorities.has(value.priority as Priority)) throw new RobotError('INVALID_COMMAND');
    if (typeof value.data !== 'object' || value.data === null || Array.isArray(value.data)) throw new RobotError('INVALID_COMMAND');
    for (const item of Object.values(value.data)) {
      if (!['string', 'number', 'boolean'].includes(typeof item)) throw new RobotError('INVALID_COMMAND');
    }
    return {
      action: 'speak',
      template: value.template as TemplateName,
      data: value.data as Record<string, string | number | boolean>,
      priority: value.priority as Priority,
    };
  }
  if (value.action === 'status' || value.action === 'stop') {
    if (!exactKeys(value, ['action', 'traceId']) || typeof value.traceId !== 'string' || !traceIdPattern.test(value.traceId)) {
      throw new RobotError('INVALID_COMMAND');
    }
    return { action: value.action, traceId: value.traceId };
  }
  throw new RobotError('INVALID_COMMAND');
}

export function createAiGateway(adapter: A3RobotAdapter) {
  return async function execute(input: unknown): Promise<GatewayResult> {
    try {
      const command = parseCommand(input);
      if (command.action === 'speak') {
        const result = await adapter.speak(command.template, command.data, command.priority);
        return { ok: true, action: 'speak', ...result };
      }
      if (command.action === 'status') {
        const status = await adapter.getStatus(command.traceId);
        return { ok: true, action: 'status', traceId: command.traceId, status };
      }
      await adapter.stop(command.traceId);
      return { ok: true, action: 'stop', traceId: command.traceId };
    } catch (error) {
      return { ok: false, error: error instanceof RobotError ? error.code : 'ROBOT_PROTOCOL_ERROR' };
    }
  };
}
