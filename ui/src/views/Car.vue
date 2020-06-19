<template>
  <div id="editCarDiv" class="carEditor">
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

    <button id="saveBtn" @click="save">Add new</button>

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
    created: function() {
        if (this.$route.params.pathMatch){
            var car = this.loadCarFromDB(this.$route.params.pathMatch)
            if (car) {
                this.loadCar(car)
            }
        }
    },
    methods: {
        save(){
            this.errorMsg = null;

            if (this.$route.params.pathMatch)
            {
                API.put('carsHandler', '/' + this.$route.params.pathMatch, {
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
            else
            {
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
        setUIToReadonly(){
            document.getElementById('saveBtn').remove();

            let inputs = document.getElementById('editCarDiv').getElementsByTagName('input');
            for(let i = 0; i < inputs.length; i++) {
                inputs[i].disabled = true;
            }
        },
        setUIToEditMode() {
            document.getElementById('saveBtn').textContent='Edit'
        },
        loadCar(car) {
            this.car.title = car.carTitle,
            this.car.description = car.carDescription;
            this.car.engine = car.engine;
            this.car.horsePower = car.horsePower;
            this.car.mileage = car.mileage;
            this.car.productionYear = car.year;
            
            if (this.$store.state.user == null || car.ownerId.localeCompare(this.$store.state.user.attributes.sub)) {
                this.setUIToReadonly();
            }
            else {
                this.setUIToEditMode();
            }
        },
        loadCarFromDB(carId) {
            return API.get('carsGetHandler', '/' + carId)
            .then(response => {
                this.loadCar(response);
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