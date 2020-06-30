<template>
  <div id="range-filter">
    <label>{{ label }}:</label>
    <input ref="valueFrom" :value="value.from" @input="updateRange" placeholder="from" />
    <span> - </span>
    <input ref="valueTo" :value="value.to" @input="updateRange" placeholder="to" />
  </div>
</template>

<script>
export default {
  name: 'RangeFilter',
  props: {
    label: String,
    value: Object
  },
  methods: {
    updateRange: async function() {
      this.$emit('input', {
        from: this.$refs.valueFrom.value,
        to: this.$refs.valueTo.value
      });
    },
  }
}
</script>

<style scoped lang="scss">
#range-filter {
  display: flex;
  justify-content: center;
  align-items: center;

  label {
    font-weight: bold;
    margin-right: 1em;
  }

  input {
    text-align: center;
    width: 100px;
  }
}
</style>