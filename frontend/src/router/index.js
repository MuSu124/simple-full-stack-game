import { createRouter, createWebHistory } from 'vue-router'

import LoginPage from '../LoginPage.vue'
import CharacterPage from '../CharacterPage.vue'
import MonsterPage from '../MonsterPage.vue'
//相对路径现在写的是../xxxPage, 但是之后这些page会放到views文件夹中，所以路径会变成@/views/xxxPage.vue

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      redirect: '/login',
    },
    {
      path: '/login',
      component: LoginPage,
    },
    {
      path: '/characters',
      component: CharacterPage,
    },
    {
      path: '/monsters',
      name: 'monsters',
      component: MonsterPage,
    },
  ],
})

export default router
