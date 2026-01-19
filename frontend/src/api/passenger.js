import apiClient from './index';

export const getPassengers = (params) => apiClient.get('/v1/passengers/', { params });
export const createPassenger = (data) => apiClient.post('/v1/passengers/', data);
export const updatePassenger = (id, data) => apiClient.put(`/v1/passengers/${id}`, data);
export const deletePassenger = (id) => apiClient.delete(`/v1/passengers/${id}`);
