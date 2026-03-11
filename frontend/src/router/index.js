import {createRouter, createWebHistory} from 'vue-router';

const routes = [
    {path: '/', name: 'auth', component: () => import('../views/AuthView.vue')},
    {path: '/menu', name: 'menu', component: () => import('../views/MenuView.vue')},
    {path: '/platforms', name: 'platforms', component: () => import('../views/PlatformsView.vue')},
    {path: '/platforms/new', name: 'platform-new', component: () => import('../views/PlatformEditView.vue')},
    {
        path: '/platforms/edit/:id',
        name: 'platform-edit',
        component: () => import('../views/PlatformEditView.vue'),
        props: true
    },
    {
        path: '/platforms/:platformId/accounts',
        name: 'accounts',
        component: () => import('../views/AccountsView.vue'),
        props: true
    },
    {
        path: '/accounts/:accountId',
        name: 'account-detail',
        component: () => import('../views/AccountDetailView.vue'),
        props: true
    },
    {
        path: '/accounts/edit/:accountId',
        name: 'account-edit',
        component: () => import('../views/AccountEditView.vue'),
        props: true
    },
    {
        path: '/accounts/new/:platformId',
        name: 'account-new',
        component: () => import('../views/AccountEditView.vue'),
        props: true
    },
];

export default createRouter({
    history: createWebHistory(),
    routes,
});