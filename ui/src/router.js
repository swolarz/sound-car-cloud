import Vue from 'vue'
import Router from 'vue-router'
import Home from './views/Home.vue'
import Secret from './views/Secret.vue'
import SignUp from './components/SignUp.vue'
import Upload from './views/Upload.vue'
import Car from './views/Car.vue'


Vue.use(Router)

const router = new Router({
  mode: 'history',
  base: process.env.BASE_URL,
  routes: [
    {
      path: '/',
      name: 'home',
      component: Home
    },
    {
      path: '/secret',
      name: 'secret',
      component: Secret,
      meta: { requiresAuth: true}
    },
    {
      path: '/upload',
      name: 'upload',
      component: Upload,
      meta: { requiresAuth: true}
    },
    {
      path: '/signUp',
      name: 'signUp',
      component: SignUp,
      meta: { forUnauthorized: true} 
    },
    {
      path: '/cars/*',
      name: 'cars',
      component: Car,
      meta: { requiresAuth: true}
    },
  ]
})


router.beforeResolve((to, from, next) => {
  if (to.matched.some(record => record.meta.requiresAuth)) {
    Vue.prototype.$Amplify.Auth.currentAuthenticatedUser().then((data) => {
      if (data && data.signInUserSession) {
        next();
      } 
    }).catch((e) => {
      console.log(e);
      next({path:'/'});
    });
  } else if (to.matched.some(record => record.meta.forUnauthorized)) {
    Vue.prototype.$Amplify.Auth.currentAuthenticatedUser().then((data) => {
      if (data && data.signInUserSession) {
        next({path:'/'});
      } 
    }).catch((e) => {
      console.log(e)
    });
    next();
  } else {
  next()
  }
})



export default router;