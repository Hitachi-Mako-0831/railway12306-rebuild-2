import { createRouter, createWebHistory } from 'vue-router';
import HomePage from '../views/HomePage.vue';
import LeftTicketSingle from '../views/ticket/LeftTicketSingle.vue';
import LeftTicketRound from '../views/ticket/LeftTicketRound.vue';
import OrderConfirm from '../views/order/OrderConfirm.vue';
import LoginPage from '../views/auth/LoginPage.vue';
import RegisterPage from '../views/auth/RegisterPage.vue';
import ForgotPasswordPage from '../views/auth/ForgotPasswordPage.vue';

const routes = [
  {
    path: '/',
    name: 'Home',
    component: HomePage
  },
  {
    path: '/leftTicket/single',
    name: 'LeftTicketSingle',
    component: LeftTicketSingle
  },
  {
    path: '/leftTicket/round',
    name: 'LeftTicketRound',
    component: LeftTicketRound
  },
  {
    path: '/order/confirm',
    name: 'OrderConfirm',
    component: OrderConfirm
  },
  {
    path: '/login',
    name: 'Login',
    component: LoginPage
  },
  {
    path: '/register',
    name: 'Register',
    component: RegisterPage
  },
  {
    path: '/forgot-password',
    name: 'ForgotPassword',
    component: ForgotPasswordPage
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

export default router;
