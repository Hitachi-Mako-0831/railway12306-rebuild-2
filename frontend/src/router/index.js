import { createRouter, createWebHistory } from 'vue-router';
import HomePage from '../views/HomePage.vue';
import LeftTicketSingle from '../views/ticket/LeftTicketSingle.vue';
import LeftTicketRound from '../views/ticket/LeftTicketRound.vue';
import OrderConfirm from '../views/order/OrderConfirm.vue';

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
  },
  {
    path: '/user/orders',
    name: 'UserOrders',
    component: () => import('../views/user/OrderPage.vue')
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

export default router;
