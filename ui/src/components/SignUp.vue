<template>
<div>
<div v-if="!user">
    <h1>Sign Up</h1>
    <input v-model="login" type="text" placeholder="Login"><br> 
    <input v-model="password" type="password" placeholder="Password"> <br>
    <input v-model="email" type="email" placeholder="Email"><br> 
    <button @click="submit">Submit</button>

</div>
<div v-if="user">
<h2>Confirm Sign Up</h2>
<input v-model="code" type="text" placeholder="Code"><br> 
<button @click="confirm">Submit</button>
</div>
<ErrorDisplayer v-bind:errorMsg="errorMsg" />
</div>
</template>
<script>
import { Auth } from 'aws-amplify';
import ErrorDisplayer from '@/components/ErrorDisplayer.vue'
export default {
    data(){
        return {
            login: '',
            email: '',
            password: '',
            code: '',
            user: '',
            errorMsg: null
        }
    },
    components: {
        ErrorDisplayer
    },
    methods: {
        confirm() {
            // After retrieveing the confirmation code from the user
            this.errorMsg = null;
            Auth.confirmSignUp(this.login, this.code, {
                // Optional. Force user confirmation irrespective of existing alias. By default set to True.
                forceAliasCreation: true
            }).then(this.$router.push("/"))
              .catch(err => this.errorMsg = err.message );
        },
        submit(){
            this.errorMsg = null;
            Auth.signUp({
                username: this.login,
                password: this.password,
                attributes: {
                    email: this.email
                },
                validationData: [],  // optional
                })
                .then(data => this.user = data.user)
                .catch(err => this.errorMsg = err.message);
        }
    }
    
}
</script>
<style>
input {
    margin: 10px;
    padding: 16px;
}
</style>