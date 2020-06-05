<template>
  <div class="login">
    <div v-if="!signedIn">
      <input v-model="login" type="text" name="" placeholder="Login" ><br>
      <input v-model="password" type="password" name="" placeholder="Password" ><br>
      <button @click="signIn">Sign in</button>
    </div>
    <div v-if="signedIn">
      <button @click="signOut">Sign Out</button>
    </div>
    <ErrorDisplayer v-bind:errorMsg="errorMsg" />
  </div>
</template>

<script>
import { Auth } from 'aws-amplify'
import { AmplifyEventBus } from 'aws-amplify-vue';
import ErrorDisplayer from '@/components/ErrorDisplayer.vue'
export default {
  name: 'Login',
  data() {
    return {
      login: '',
      password: '',
      errorMsg: null
    }
  },
  props: {
    msg: String,
  },
  components: {
        ErrorDisplayer
    },
  created(){
    this.errorMsg = null;
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
  computed: {
    signedIn(){
      return this.$store.state.signedIn;
    }
  },
  methods: {
    signIn(){
      this.errorMsg = null;
      Auth.signIn(this.login, this.password)
        .then(user =>{
            this.$store.state.signedIn = !!user;
            this.$store.state.user = user;
        } )
        .catch(err => this.errorMsg = err.message);
    },
    signOut() {
      this.errorMsg = null;
      Auth.signOut()
        .then(data =>{
          this.$store.state.signedIn = !!data;
        } )
        .catch(err => this.errorMsg = err.message);
    },
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

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped lang="scss">
input {
  padding: 16px;
  margin: 10px;
}
h3 {
  margin: 40px 0 0;
}
ul {
  list-style-type: none;
  padding: 0;
}
li {
  display: inline-block;
  margin: 0 10px;
}
a {
  color: #42b983;
}
</style>