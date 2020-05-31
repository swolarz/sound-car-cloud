<template>
    <div v-if="errorMsg" class="error">
        <span>{{ errorMsg }}</span>
    </div>
</template>

<script>
export default {
  name: 'ErrorDisplayer',
  props: {
    errorMsg: String,
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped lang="scss">
.error {
  color: red;
}
</style>