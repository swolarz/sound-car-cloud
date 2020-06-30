<template>
  <div id="cars-filtered-list">
    <div id="cars-status-message">
      <StatusMessage v-model="searchStatus" />
    </div>
    <div id="cars-filter">
      <div id="search-bar">
        <input v-model="searchPhrase" placeholder="Search phrase" />
      </div>
      <div id="attribute-filters">
        <div id="horse-power-filter">
          <RangeFilter label="Horse power" v-model="horsePower"  />
        </div>
        <div id="mileage-filter">
          <RangeFilter label="Mileage" v-model="mileage" />
        </div>
        <div id="car-year-filter">
          <RangeFilter label="Year" v-model="carYear" />
        </div>
        <!-- <div v-if="">
          <label>Show only mine</label>
          <input type="checkbox" v-model="onlyUserCars">
        </div> -->
      </div>
      <div id="search-button">
        <router-link :to="searchUrl" v-on:click="loadCars()" tag="button">Search</router-link>
      </div>
    </div>
    <div id="cars-pager">
    </div>
    <div id="cars-list">
      <CarsList v-bind:cars="cars" />
    </div>
  </div>
</template>

<script>
import CarsList from './CarsList';
import RangeFilter from '../filter/RangeFilter';
import StatusMessage from '../StatusMessage';
import SuperCars from './MockCars';
import { API } from "aws-amplify";

export default {
  name: "CarsFilteredList",
  components: {
    CarsList,
    RangeFilter,
    StatusMessage
  },
  data: function() {
    return {
      cars: [],
      searchPhrase: '',
      horsePower: {
        from: '',
        to: ''
      },
      mileage: {
        from: '',
        to: ''
      },
      carYear: {
        from: '',
        to: ''
      },
      // onlyUserCars: false,
      totalCars: 0,
      page: 0,
      perPage: 10,
      searchStatus: {
        status: '',
        message: ''
      }
    }
  },
  computed: {
    searchUrl: function() {
      let target = `/search?page=${this.page}&perPage=${this.perPage}`;

      if (this.searchPhrase) target += `&q=${this.searchPhrase}`;
      if (this.horsePower.from) target += `&hpl=${this.horsePower.from}`;
      if (this.horsePower.to) target += `&hpu=${this.horsePower.to}`;
      if (this.mileage.from) target += `&ml=${this.mileage.from}`;
      if (this.mileage.to) target += `&mu=${this.mileage.to}`;
      if (this.carYear.from) target += `&cyl=${this.carYear.from}`;
      if (this.carYear.to) target += `&cyu=${this.carYear.to}`;

      return target;
    }
  },
  created: function() {
    this.loadFilterParams();
    this.loadCars();
  },
  watch: {
    '$route.query'() {
      this.loadFilterParams();
      this.loadCars();
    }
  },
  methods: {
    loadCars: async function() {
      let valid = await this.validateFilters();
      if (!valid) {
        return;
      }

      let params = {};
      if (this.searchPhrase) params.q = this.searchPhrase;
      if (this.horsePower.from) params.horsePowerFrom = parseInt(this.horsePower.from);
      if (this.horsePower.to) params.horsePowerTo = parseInt(this.horsePower.to);
      if (this.mileage.from) params.mileageFrom = parseInt(this.mileage.from);
      if (this.mileage.to) params.mileageTo = parseInt(this.mileage.to);
      if (this.carYear.from) params.yearFrom = parseInt(this.carYear.from);
      if (this.carYear.to) params.yearTo = parseInt(this.carYear.to);

      params.page = this.page;
      params.perPage = this.perPage;

      this.cars = SuperCars.mocks;

      API.get('carFetch', '', { queryStringParameters: params })
        .then(response => {
          this.totalCars = response.total;
          if (response.results,length) {
            this.cars = response.results.length;
          }
          console.log('Search results: ', response);
          this.setStatus('success', 'Twoje Samochodziki!');
        })
        .catch(error => {
          console.log('Error: ', error);
          this.setStatus('error', error.message);
        });
    },
    loadFilterParams: function() {
      this.page = this.$route.query.page || 0;
      this.perPage = this.$route.query.perPage || 10;
      this.searchPhrase = this.$route.query.q || '';
      this.horsePower = {
        from: this.$route.query.hpl || '',
        to: this.$route.query.hpu || ''
      };
      this.mileage = {
        from: this.$route.query.ml || '',
        to: this.$route.query.mu || ''
      };
      this.carYear = {
        from: this.$route.query.cyl || '',
        to: this.$route.query.cyu || ''
      };
    },
    validateFilters: async function() {
      if (this.searchPhrase.length > 400) {
        this.setStatus('error', 'Query phrase cannot exceed 400 characters');
        return false;
      }

      if (!this.isValidPositive(this.horsePower.from)) {
        this.setStatus('error', `Invalid lower-bound horse power value: ${this.horsePower.from}`);
        return false;
      }
      if (!this.isValidPositive(this.horsePower.to)) {
        this.setStatus('error', `Invalid upper-bound horse power value: ${this.horsePower.to}`);
        return false;
      }

      if (!this.isValidPositive(this.mileage.from)) {
        this.setStatus('error', `Invalid lower-bound mileage value: ${this.mileage.from}`);
        return false;
      }
      if (!this.isValidPositive(this.mileage.to)) {
        this.setStatus('error', `Invalid upper-bound mileage value: ${this.mileage.to}`);
        return false;
      }

      if (!this.isValidPositive(this.carYear.from)) {
        this.setStatus('error', `Invalid lower-bound car year value: ${this.carYear.from}`);
        return false;
      }
      if (!this.isValidPositive(this.carYear.to)) {
        this.setStatus('error', `Invalid upper-bound car year value: ${this.carYear.to}`);
        return false;
      }

      return true;
    },
    isValidPositive: function(text) {
      if (!text) return true;

      let num = parseInt(text, 10);
      return (text !== 'NaN' && num == text && num >= 0);
    },
    setStatus: async function(status, message) {
      this.searchStatus = {
        status: status,
        message: message
      };
    },
    clearStatus: async function() {
      await this.setStatus('', '');
    }
  }
}
</script>

<style scoped lang="scss">
#cars-filtered-list {
  display: flex;
  flex-direction: column;
  align-items: center;

  #cars-status-message {
    width: 50%;
  }

  #cars-filter {
    display: flex;
    flex-direction: column;
    align-items: stretch;

    width: 50%;

    border-bottom-style: solid;

    #search-bar {
      input {
        width: 75%;
      }
    }
    #search-button {
      align-self: center;
      margin: 2em;

      button {
        width: 100px;
        height: 40px;
      }
    }

    label {
      font-weight: bold;
      margin-right: 1em;
    }
  }

  #cars-list {
    width: 50%;
  }
}
</style>