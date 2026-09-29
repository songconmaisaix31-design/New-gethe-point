export const templateNames = [
  'care_reminder',
  'escalation',
  'handover_confirm',
] as const;

export type TemplateName = (typeof templateNames)[number];
export type Priority = 'normal' | 'high' | 'urgent';

export type SpeakCommand = {
  action: 'speak';
  template: TemplateName;
  data: Record<string, string | number | boolean>;
  priority: Priority;
};

export type StatusCommand = { action: 'status'; traceId: string };
export type StopCommand = { action: 'stop'; traceId: string };
export type RobotCommand = SpeakCommand | StatusCommand | StopCommand;

export type AudioStatus =
  | 'TTSConfigStatusType_Unknown'
  | 'TTSStatusType_Begin'
  | 'TTSStatusType_Playing'
  | 'TTSStatusType_End'
  | 'TTSStatusType_Stop'
  | 'TTSStatusType_Error'
  | 'TTSStatusType_InQue'
  | 'TTSStatusType_NOTInQue';

export type GatewayResult =
  | {
      ok: true;
      action: 'speak';
      traceId: string;
      remoteTraceId?: string;
      terminalStatus: AudioStatus;
    }
  | { ok: true; action: 'status'; traceId: string; status: AudioStatus }
  | { ok: true; action: 'stop'; traceId: string }
  | { ok: false; error: RobotErrorCode };

export type RobotErrorCode =
  | 'INVALID_COMMAND'
  | 'UNAUTHORIZED'
  | 'ROBOT_DISABLED'
  | 'TTS_TEXT_TOO_LONG'
  | 'ROBOT_UNREACHABLE'
  | 'ROBOT_PROTOCOL_ERROR'
  | 'PLAYBACK_ERROR'
  | 'PLAYBACK_TIMEOUT';

export class RobotError extends Error {
  readonly code: RobotErrorCode;

  constructor(code: RobotErrorCode) {
    super(code);
    this.name = 'RobotError';
    this.code = code;
  }
}
