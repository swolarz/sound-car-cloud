import Vue from 'vue'
import Router from 'vue-router'
import Home from './views/Home.vue'
import SignUp from './components/SignUp';
import Login from './components/Login';
import Logout from './components/Logout';
import Car from './views/Car.vue'


Vue.use(Router)

const router = new Router({
  mode: 'history',
  base: process.env.BASE_URL,
  routes: [
    {
      path: '/',
      name: 'index',
      component: Home
    },
    {
      path: '/home',
      name: 'home',
      component: Home
    },
    {
      path: '/signIn',
      name: 'signIn',
      component: Login
    },
    {
      path: '/signUp',
      name: 'signUp',
      component: SignUp,
      meta: { forUnauthorized: true } 
    },
    {
      path: '/signOut',
      name: 'signOut',
      component: Logout
    },
    {
      path: '/cars/*',
      name: 'cars',
      component: Car
    },
    {
      path: '/cars',
      name: 'addCar',
      component: Car
    }
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