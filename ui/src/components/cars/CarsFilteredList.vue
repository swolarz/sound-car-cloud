<template>
  <div id="cars-filtered-list">
    <div id="cars-status-message">
      <StatusMessage v-model="searchStatus" />
    </div>
    <div id="cars-filter">
      <div id="search-bar">
        <b-form-input v-model="searchPhrase" placeholder="Search phrase" />
        <b-icon-search class="h2" />
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
        <router-link :to="searchUrl" tag="button">Search</router-link>
      </div>
    </div>
    <div id="cars-pager">
      <div class="cars-count">
        <label>Total results:</label>
        <span>{{ totalCars }}</span>
      </div>
      <div>
        <b-pagination v-model="page" :totalRows="totalCars" :per-page="perPage"></b-pagination>
      </div>
    </div>
    <div id="cars-list-container">
      <CarsList v-bind:cars="cars" />
    </div>
  </div>
</template>

<script>
import CarsList from './CarsList';
import RangeFilter from '../filter/RangeFilter';
import StatusMessage from '../StatusMessage';
// import SuperCars from './MockCars';
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
      page: 1,
      perPage: 10,
      searchStatus: {
        status: '',
        message: ''
      }
    }
  },
  computed: {
    searchUrl: function() {
      let params = {
        page: this.page,
        perPage: this.perPage
      };

      if (this.searchPhrase) params.q = this.searchPhrase;
      if (this.horsePower.from) params.hpl = this.horsePower.from;
      if (this.horsePower.to) params.hpu = this.horsePower.to;
      if (this.mileage.from) params.ml = this.mileage.from;
      if (this.mileage.to) params.mu = this.mileage.to;
      if (this.carYear.from) params.cyl = this.carYear.from;
      if (this.carYear.to) params.cyu = this.carYear.to;

      return {
        path: '/home',
        query: params
      };
    },
    pagesTotal: function() {
      return Math.ceil(this.page / this.perPage);
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

      params.page = this.page - 1;
      params.perPage = this.perPage;

      this.cars = []; // SuperCars.mocks;

      API.get('carFetch', '', { queryStringParameters: params })
        .then(response => {
          this.totalCars = response.total;
          if (response.results.length) {
            this.cars = response.results;
          }
          console.log('Search results: ', response);
        })
        .catch(error => {
          console.log('Error: ', error);
          this.setStatus('error', error.message);
        });
    },
    loadFilterParams: function() {
      this.page = parseInt(this.$route.query.page, 10) || 1;
      this.perPage = parseInt(this.$route.query.perPage, 10) || 10;
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
    min-width: 100%;
  }

  #cars-filter {
    display: flex;
    flex-direction: column;
    align-items: stretch;

    margin-top: 1em;
    padding: 1em;
    min-width: 50%;

    border-top-style: solid;
    border-bottom-style: solid;
    border-color: darkblue;

    #search-bar {
      display: flex;
      align-items: center;

      input {
        min-width: 50%;
        margin-right: 0.5em;
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

  #cars-pager {
    display: flex;
    flex-direction: column;

    .cars-count {
      margin: 1em;

      label {
        margin-right: 1em;
        font-weight: bold;
      }
    }
  }

  #cars-list-container {
    min-width: 100%;
    padding: 1em;
  }
}
</style>