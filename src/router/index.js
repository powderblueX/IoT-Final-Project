import { createRouter, createWebHistory } from 'vue-router';

const router = createRouter({
    history: createWebHistory(import.meta.env.BASE_URL),
    routes: [
        {
            path: '/',
            name: 'Main',
            component: () => import('@/views/MainPage.vue'),
            children: [
                {
                    path: '/',
                    name: 'Subscriber',
                    component: () => import('@/views/subscriber/Subscriber.vue'),
                },
                {
                    path: '/dataProcessor',
                    name: 'DataProcessor',
                    component: () => import('@/views/DataProcessor/DataProcessor.vue')
                }
            ]
        },
    ]
})

export default router