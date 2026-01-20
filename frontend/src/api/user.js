import apiClient from './index.js';

export function getProfile() {
  return apiClient.get('/v1/users/profile');
}

export function updateProfile(payload) {
  return apiClient.put('/v1/users/profile', payload);
}
