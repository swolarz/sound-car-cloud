<template>
  <div id="range-filter">
    <label>{{ label }}:</label>
    <b-form-input class="range-input" v-model="valueFrom" @input="updateRange" placeholder="from" />
    <span> - </span>
    <b-form-input class="range-input" v-model="valueTo" @input="updateRange" placeholder="to" />
  </div>
</template>

<script>
export default {
  name: 'RangeFilter',
  props: {
    label: String,
    value: Object
  },
  data: function() {
    return {
      valueFrom: this.value.from,
      valueTo: this.value.to
    };
  },
  methods: {
    updateRange: async function() {
      this.$emit('input', {
        from: this.valueFrom,
        to: this.valueTo
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

  padding: 1em;

  label {
    font-weight: bold;
    margin-right: 1em;
  }

  .range-input {
    text-align: center;
    width: 150px;
    margin-right: 1em;
    margin-left: 1em;
  }
}
</style>