import { spawn } from 'node:child_process';

const port = 18787;
const child = spawn(process.execPath, ['src/server.ts'], {
  cwd: new URL('..', import.meta.url),
  env: { ...process.env, ROBOT_MODE: 'mock', ROBOT_GATEWAY_PORT: String(port) },
  stdio: ['ignore', 'pipe', 'inherit'],
});

try {
  await new Promise((resolve, reject) => {
    const timeout = setTimeout(() => reject(new Error('Server startup timed out')), 5_000);
    child.once('exit', (code) => reject(new Error(`Server exited with code ${code}`)));
    child.stdout.once('data', () => {
      clearTimeout(timeout);
      resolve();
    });
  });
  const response = await fetch(`http://127.0.0.1:${port}/v1/robot/commands`, {
    method: 'POST',
    headers: { 'content-type': 'application/json' },
    body: JSON.stringify({
      action: 'speak',
      template: 'care_reminder',
      data: { title: 'Medicine', instruction: 'Take it after the meal' },
      priority: 'normal',
    }),
  });
  const result = await response.json();
  if (!response.ok || result.ok !== true || result.terminalStatus !== 'TTSStatusType_NOTInQue') {
    throw new Error(`Unexpected smoke result: ${JSON.stringify(result)}`);
  }
  process.stdout.write('SMOKE_OK mock speak reached terminal status\n');
} finally {
  child.kill('SIGTERM');
}

