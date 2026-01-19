import { defineStore } from 'pinia';

export const useUserStore = defineStore('user', {
  state: () => ({
    token: '',
    username: '',
  }),
  getters: {
    isAuthenticated: (state) => !!state.token,
  },
  actions: {
    setAuth(token, username) {
      this.token = token;
      this.username = username;
    },
    clearAuth() {
      this.token = '';
      this.username = '';
    },
  },
  persist: true,
});

