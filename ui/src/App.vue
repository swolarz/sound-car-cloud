<template>
  <div id="app">
    <div id="nav">
      <router-link to="/">Home</router-link> |
      <router-link v-if="this.$store.state.signedIn" to="/secret">Secret</router-link> |
      <router-link v-if="this.$store.state.signedIn" to="/upload">Upload</router-link> |
      <router-link v-if="this.$store.state.signedIn" to="/cars/">Add car</router-link>
      <router-link v-if="!this.$store.state.signedIn" to="/signUp">SignUp</router-link>
    </div>
    <router-view/>
  </div>
</template>

<script>
import { Auth } from 'aws-amplify'
import { AmplifyEventBus } from 'aws-amplify-vue';

export default {
  name: 'app',
  created: function () {
    this.findUser();
    AmplifyEventBus.$on('authState', info => {
      if(info === "signedIn") {
        this.findUser();
      } else {
        this.$store.state.signedIn = false;
        this.$store.state.user = null;
      }
    });
  },
  methods: {
    async findUser() {
      try {
        const user = await Auth.currentAuthenticatedUser();
        this.$store.state.signedIn = true;
        this.$store.state.user = user;
      } catch(err) {
        this.$store.state.signedIn = false;
        this.$store.state.user = null;
      }
    }
  }
}
</script>

<style lang="scss">
#app {
  font-family: 'Avenir', Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
}
#nav {
  padding: 30px;
  a {
    font-weight: bold;
    color: #2c3e50;
    &.router-link-exact-active {
      color: #42b983;
    }
  }
}
</style>