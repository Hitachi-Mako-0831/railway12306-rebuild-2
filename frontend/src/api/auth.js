import apiClient from './index.js';

export function login(payload) {
  return apiClient.post('/v1/login', payload);
}

export function register(payload) {
  return apiClient.post('/v1/register', payload);
}

export function resetPassword(payload) {
  return apiClient.post('/v1/auth/password/recovery/reset', payload);
}
