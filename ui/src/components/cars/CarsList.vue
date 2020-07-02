<template>
  <div class="cars-list">
    <div v-if="cars && cars.length">
      <ul>
        <li v-bind:key="car.id" v-for="car in cars">
          <CarItem v-bind:car="car" />
        </li>
      </ul>
    </div>
    <div v-if="!(cars && cars.length)" class="no-cars">
      <h3>Unfortunately, no results found...</h3>
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

<style scoped lang="scss">
.cars-list {
  ul {
    list-style-type: none;
    padding: 0;
  }

  .no-cars {
    padding: 3em;
  }
}
</style>