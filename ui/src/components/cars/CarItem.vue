<template>
  <div class="car-item">
    <div class="car-image">
      <img :src="car.photoUrl" />
    </div>
    <div class="car-info">
      <div class="car-header">
        <div class="car-title">
          <h2>{{ car.carTitle }}</h2>
        </div>
        <div class="car-owner">
          <h4>{{ car.owner.name }}</h4>
        </div>
      </div>
      <div class="car-intro">
        <p>{{ car.carIntro }}</p>
      </div>
      <div class="car-data">
        <div class="car-attributes">
          <div v-if="car.engine" class="car-attr">
            <label>Engine:</label>
            <span>{{ car.engine }}</span>
          </div>
          <div v-if="car.horsePower" class="car-attr">
            <label>Horse power:</label>
            <span>{{ car.horsePower }}</span>
          </div>
          <div v-if="car.year" class="car-attr">
            <label>Year:</label>
            <span>{{ car.year }}</span>
          </div>
          <div v-if="car.mileage" class="car-attr">
            <label>Mileage:</label>
            <span>{{ car.mileage }}</span>
          </div>
        </div>
        <div class="car-link">
          <router-link :to="carDetailsUrl">
            Car details
            <b-icon-chevron-compact-right />
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'CarItem',
  props: {
    car: Object
  },
  computed: {
    carDetailsUrl: function() {
      return {
        path: '/cars/' + this.car.id
      };
    }
  }
}
</script>

<style scoped lang="scss">
.car-item {
  display: flex;
  border-style: solid;
  
  padding: 0.5em;
  margin-top: 1em;
  margin-bottom: 1em;

  h2 {
    margin: 0;
  }

  h3 {
    margin: 0;
  }

  .car-image {
    flex: 4;

    img {
      width: 100%;
    }
  }

  .car-info {
    flex: 8;
    display: flex;
    flex-direction: column;

    .car-header {
      display: flex;

      margin: 1em;
      margin-left: 2em;

      .car-title {
        flex-grow: 1;
        text-align: start;
        font-weight: bold;
      }

      .car-owner {
        font-style: italic;
      }
    }

    .car-intro {
      margin: 1em;
      margin-left: 2em;
      margin-top: 0;

      p {
        text-align: start;
        margin: 0;
      }
    }

    .car-data {
      display: flex;
      flex-grow: 1;

      padding: 1em;

      .car-link {
        align-self: flex-end;
      }

      .car-attributes {
        flex-grow: 1;
        display: flex;
        flex-direction: column;
        align-items: flex-start;

        margin-left: 2em;

        .car-attr {
          font-size: 0.75em;
          padding: 0;

          label {
            margin-right: 1em;
            font-weight: bold;
          }
        }
      }
    }
  }
}
</style>