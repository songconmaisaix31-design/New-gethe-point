import { Buffer } from 'node:buffer';
import type { A3Client } from './a3-client.ts';
import { RobotError, type Priority, type TemplateName } from './contracts.ts';

const templates: Record<TemplateName, { fields: readonly string[]; render: (data: Record<string, string>) => string }> = {
  care_reminder: {
    fields: ['title', 'instruction'],
    render: ({ title, instruction }) => `${title}时间到了，${instruction}`,
  },
  escalation: {
    fields: ['subjectName', 'title'],
    render: ({ subjectName, title }) => `紧急提醒：${subjectName}的${title}尚未处理，请尽快查看。`,
  },
  handover_confirm: {
    fields: ['domainName'],
    render: ({ domainName }) => `您有一个新的责任域交接待确认：${domainName}。`,
  },
};

export type AdapterOptions = {
  client: A3Client;
  mode: 'mock' | 'real';
  enabled: boolean;
};

function renderTemplate(template: TemplateName, rawData: Record<string, string | number | boolean>): string {
  const definition = templates[template];
  const actualKeys = Object.keys(rawData).sort();
  const expectedKeys = [...definition.fields].sort();
  if (actualKeys.length !== expectedKeys.length || actualKeys.some((key, index) => key !== expectedKeys[index])) {
    throw new RobotError('INVALID_COMMAND');
  }
  const data: Record<string, string> = {};
  for (const field of definition.fields) {
    const value = String(rawData[field]).trim();
    if (value.length === 0 || /[\u0000-\u001f\u007f]/u.test(value)) {
      throw new RobotError('INVALID_COMMAND');
    }
    data[field] = value;
  }
  const text = definition.render(data);
  if (Buffer.byteLength(text, 'utf8') > 1_024) {
    throw new RobotError('TTS_TEXT_TOO_LONG');
  }
  return text;
}

export function createA3RobotAdapter(options: AdapterOptions) {
  let announcementTail = Promise.resolve();

  function speak(template: TemplateName, data: Record<string, string | number | boolean>, priority: Priority) {
    if (options.mode === 'real' && !options.enabled) {
      return Promise.reject(new RobotError('ROBOT_DISABLED'));
    }
    const text = renderTemplate(template, data);
    const task = announcementTail.then(() => options.client.playAndWait(text, priority));
    announcementTail = task.then(() => undefined, () => undefined);
    return task;
  }

  return {
    speak,
    getStatus: options.client.getStatus,
    stop: options.client.stop,
  };
}

export type A3RobotAdapter = ReturnType<typeof createA3RobotAdapter>;
