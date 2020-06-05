<template>
  <div class="secret">
    <h1>This is Server Information</h1>
    <button @click="performTestRequest">Test</button>
    <p>{{ lambdaMsg }}</p>
  </div>
</template>

<script>
// @ is an alias to /src
import { API } from "aws-amplify";

export default {
  name: 'secret',
  data() {
    return { lambdaMsg: "Click to get a message" }
  },
  methods: {
    async performTestRequest(){
      API.get("hello", "")
      .then(response => {
        this.lambdaMsg = response.message;
      })
      .catch(error => {
        console.log(error);
      });
    }
  }
}
</script>