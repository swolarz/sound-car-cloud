<template>
  <div>
    <div v-if="cars && cars.length">
      <ul>
        <li v-bind:key="car.id" v-for="car in cars">
          <CarItem v-bind:car="car" />
        </li>
      </ul>
    </div>
    <div v-if="!(cars && cars.length)">
      <h2>Unfortunately, no results found...</h2>
    </div>
  </div>
</template>

<script>
import CarItem from './CarItem';

export default {
  name: 'CarList',
  components: {
    CarItem
  },
  props: {
    cars: Array
  }
}
</script>

<style scoped>
ul {
  list-style-type: none;
  padding: 0;
}
</style>