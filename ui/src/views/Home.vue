<template>
  <div class="home">
    <CarsSearch />
  </div>
</template>

<script>
// @ is an alias to /src
import CarsSearch from '@/components/cars/CarsSearch.vue';

export default {
  name: 'home',
  components: {
    CarsSearch
  }
}
</script>