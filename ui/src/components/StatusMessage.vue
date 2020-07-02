<template>
  <div id="statusContainer" v-if="isVisible()" v-bind:class="resolveContainerClass()">
    <div id="messageContainer">
      <h3>{{ value.message }}</h3>
    </div>
    <div>
      <button v-on:click="clearMessage()">X</button>
    </div>
  </div>
</template>

<script>
export default {
  name: 'StatusMessage',
  props: {
    value: Object
  },
  methods: {
    isVisible: function() {
      return (this.value.message && ['success', 'warn', 'error'].includes(this.value.status));
    },
    resolveContainerClass: function() {
      return 'status-' + this.value.status;
    },
    clearMessage: function() {
      this.$emit('input', {
        message: '',
        status: ''
      });
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped lang="scss">
#statusContainer {
  display: flex;
  width: 100%;

  padding: 1em;

  #messageContainer {
    flex-grow: 1;
    text-align: start;
  }

  h3 {
    font-weight: bold;
    color: white;
  }

  button {
    font-weight: bold;
    color: black;
  }
}

.status-success {
  background-color: green;
}
.status-warn {
  background-color: darkorange;
}
.status-error {
  background-color: darkred;
}

</style>