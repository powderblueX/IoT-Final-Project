import { createRouter, createWebHistory } from 'vue-router';

const router = createRouter({
    history: createWebHistory(import.meta.env.BASE_URL),
    routes: [
        {
            path: '/',
            name: 'Publisher',
            component: () => import('@/views/publisher/Publisher.vue'),
        },
    ]
})

export default router