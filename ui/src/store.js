import Vue from 'vue'
import Vuex from 'vuex'

Vue.use(Vuex)

export default new Vuex.Store({
  state: {
    user: null,
    signedIn: false,
    audio: {
      orderIndex: 0
    }
  },
  mutations: {

  },
  actions: {

  }
})