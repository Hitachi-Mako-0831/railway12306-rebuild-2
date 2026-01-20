import { createRouter, createWebHistory } from 'vue-router';
import HomePage from '../views/HomePage.vue';
import LeftTicketSingle from '../views/ticket/LeftTicketSingle.vue';
import LeftTicketRound from '../views/ticket/LeftTicketRound.vue';
import OrderConfirm from '../views/order/OrderConfirm.vue';
import LoginPage from '../views/auth/LoginPage.vue';
import RegisterPage from '../views/auth/RegisterPage.vue';
import ForgotPasswordPage from '../views/auth/ForgotPasswordPage.vue';
import ProfilePage from '../views/user/ProfilePage.vue';
import PassengerPage from '../views/user/PassengerPage.vue';
import UserLayout from '../layouts/UserLayout.vue';

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
  },
  {
    path: '/profile',
    name: 'Profile',
    component: ProfilePage
  },
  {
    path: '/user',
    component: UserLayout,
    children: [
      {
        path: 'passengers',
        name: 'PassengerPage',
        component: PassengerPage
      },
      {
        path: 'orders',
        name: 'UserOrders',
        component: () => import('../views/user/OrderPage.vue')
      }
    ]
  },
  {
    path: '/order/detail/:id',
    name: 'OrderDetail',
    component: () => import('../views/order/OrderDetail.vue')
  },
  {
    path: '/order/pay/:id',
    name: 'OrderPay',
    component: () => import('../views/order/OrderPay.vue')
  },
  {
    path: '/order/success',
    name: 'OrderSuccess',
    component: () => import('../views/order/OrderSuccess.vue')
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

export default router;
