<template>
  <div id="app">
    <div id="nav">
      <div class="nav-start">
        <div >
          <router-link to="/">
            <div class="scc-logo">
              <img src="@/assets/logo.png" />
              <h1>Sound Car-Cloud</h1>
            </div>
          </router-link>
        </div>
      </div>
      <div class="nav-end">
        <div v-if="this.$store.state.signedIn" class="nav-link">
          <router-link to="/cars/">
            <div class="mb-0">
              <b-icon-file-plus />Add car
            </div>
          </router-link>
        </div>
        <div v-if="!this.$store.state.signedIn" class="nav-link">
          <router-link to="/signIn">Sign in</router-link>
        </div>
        <div v-if="!this.$store.state.signedIn" class="nav-link">
          <router-link to="/signUp">Sign up</router-link>
        </div>
        <div v-if="this.$store.state.signedIn" class="nav-link">
          <router-link to="/signOut">Sign out</router-link>
        </div>
        <div v-if="this.$store.state.signedIn" class="nav-icon">
          <b-icon-person-circle class="h3" />
        </div>
      </div>
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
  display: flex;
  min-width: 100%;

  background-color: lightskyblue;

  .nav-start {
    flex-grow: 1;
    display: flex;
  }

  .nav-end {
    display: flex;
    align-items: center;
  }

  .scc-logo {
    display: flex;
    align-items: center;

    img {
      margin: 0;
      padding: 0;
      height: 100px;
      width: 150px;
    }
    h1 {
      font-family: "Comic Sans MS", "Comic Sans", cursive;
      color: brown;
    }
  }

  .nav-icon {
    margin: 0.5em;
  }

  .nav-link {
    border-style: solid;
    border-color: lightseagreen;
    margin: 0.5em;

    a {
      font-weight: bold;
      color: #2c3e50;
      &.router-link-exact-active {
        color: #42b983;
      }
    }
  }
}
</style>