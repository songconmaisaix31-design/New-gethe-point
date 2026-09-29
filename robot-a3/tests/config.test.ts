import assert from 'node:assert/strict';
import test from 'node:test';
import { loadConfig } from '../src/config.ts';

test('defaults to mock mode on loopback', () => {
  const config = loadConfig({});
  assert.equal(config.mode, 'mock');
  assert.equal(config.enabled, false);
  assert.equal(config.gatewayHost, '127.0.0.1');
});

test('requires a token for non-loopback binding', () => {
  assert.throws(() => loadConfig({ ROBOT_GATEWAY_HOST: '0.0.0.0' }), /ROBOT_GATEWAY_TOKEN/);
});

test('rejects base URLs containing credentials or paths', () => {
  assert.throws(() => loadConfig({ ROBOT_BASE_URL: 'http://user:pass@robot.test/path' }), /ROBOT_BASE_URL/);
});
