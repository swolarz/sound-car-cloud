<template>
  <div class="carEditor">
    <p>Car title</p>
    <input v-model="car.title" type="text">

    <p>Description</p>
    <input v-model="car.description" type="text">

    <p>Engine</p>
    <input v-model="car.engine" type="text">

    <p>Horse power</p>
    <input v-model="car.horsePower" type="number">

    <p>Mileage</p>
    <input v-model="car.mileage" type="number">

    <p>Production year</p>
    <input v-model="car.productionYear" type="number">

    <button @click="save">Save</button>

    <ErrorDisplayer v-bind:errorMsg="errorMsg" />
  </div>
</template>

<script>
import ErrorDisplayer from '@/components/ErrorDisplayer.vue'
import { API } from "aws-amplify";

export default {
  name: 'car',
  data() {
        return {
            errorMsg: null,
            car: {
                title: '',
                description: '',
                engine: '',
                horsePower: '',
                mileage: '',
                productionYear: ''
            },
            
        }
    },
    methods: {
        save(){
            this.errorMsg = null;
            API.post('carsHandler', '', {
                body: {
                    'carTitle': this.car.title,
                    'carDescription': this.car.description,
                    'engine': this.car.engine,
                    'horsePower': parseInt(this.car.horsePower),
                    'mileage': parseInt(this.car.mileage),
                    'year': parseInt(this.car.productionYear),
                }
            }).then(response => {
                console.log(response);
            })
            .catch(error => {
                this.errorMsg = error.response.data.message;
            });
        }
    },
    components: {
        ErrorDisplayer
    }
}
</script>