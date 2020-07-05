<template>
  <div id="car-details-container" class="carEditor">
    <div id="car-details-status-message">
      <StatusMessage v-model="statusInfo" />
    </div>

    <div v-if="loading" class="car-loading-screen">
      <h2>{{ loaderText }}</h2>
    </div>

    <div v-if="!loading" class="car-form">
      <div class="car-details">
        <div class="car-photo">
          <div>
            <img v-if="car.photoId" :src="carPhotoUrl" />
            <img v-if="!car.photoId" src="@/assets/car-placeholder.png" />
          </div>
        </div>

        <div v-if="editMode" class="car-input car-photo-input">
          <label>Upload car photo</label>
          <PhotosUpload v-model="car.photoId" @uploaderror="onPhotoUploadError" />
        </div>

        <div v-if="editMode" class="car-input car-audio-input">
          <label>Upload engine sound</label>
          <AudioUpload v-model="car.audioId" @uploaderror="onAudioUploadError" />
        </div>

        <div class="car-input car-audio-player">
          <AudioPlayer v-bind:audioUrl="carAudioUrl" />
        </div>

        <div class="car-input car-text-input">
          <label>Car title</label>
          <b-form-input v-model="car.title" :disabled="!editMode" type="text" />
        </div>

        <div class="car-input car-text-input car-description-input">
          <label>Description</label>
          <b-form-textarea v-model="car.description" :disabled="!editMode" :rows="10" />
        </div>

        <div class="car-input car-value-input car-engine-input">
          <label>Engine</label>
          <b-form-input v-model="car.engine" :disabled="!editMode" type="text" />
          <span />
        </div>

        <div class="car-input car-value-input">
          <label>Horse power</label>
          <b-form-input v-model="car.horsePower" :disabled="!editMode" type="number" />
          <span />
        </div>

        <div class="car-input car-value-input">
          <label>Mileage</label>
          <b-form-input v-model="car.mileage" :disabled="!editMode" type="number" />
          <span class="value-measure">miles</span>
        </div>

        <div class="car-input car-value-input">
          <label>Production year</label>
          <b-form-input v-model="car.productionYear" :disabled="!editMode" type="number" />
          <span />
        </div>
      </div>
      <div v-if="editMode" class="car-edit-buttons">
        <button v-if="carId && isOwner" id="deleteButton" @click="deleteCar">Delete car</button>
        <button id="saveButton" @click="save">{{ this.saveButtonText }}</button>
      </div>
      <div v-if="!editMode && isOwner" class="car-do-edit">
        <button id="editModeButton" @click="editMode = true">Edit car data</button>
      </div>
    </div>
  </div>
</template>

<script>
import PhotosUpload from "@/components/PhotosUpload";
import AudioUpload from '@/components/AudioUpload';
import AudioPlayer from '@/components/AudioPlayer';
import StatusMessage from "@/components/StatusMessage";
import { API } from "aws-amplify";
import aws_exports from "@/autoGenConfig";
import url from "url";

export default {
  name: "car",
  data() {
    return {
      statusInfo: {
        status: "",
        error: ""
      },
      editMode: false,
      carNotFound: false,
      loading: false,
      carId: null,
      car: {
        title: "",
        description: "",
        engine: "",
        horsePower: "",
        mileage: "",
        productionYear: "",
        photoId: "",
        audioId: "",
        ownerId: ""
      }
    };
  },
  created: function() {
    this.loadCarFromLinkIfNeeded();
    if (!this.carId) {
      if (!this.$store.state.signedIn) {
        this.$router.replace('/signIn');
      }
      this.editMode = true;
    }
  },
  watch: {
    "$route.params.pathMatch": function() {
      this.loadCarFromLinkIfNeeded();
    }
  },
  computed: {
    saveButtonText: function() {
      return this.carId ? "Save" : "Save new";
    },
    isOwner: function() {
      return (this.car.ownerId && this.$store.state.signedIn && this.car.ownerId === this.$store.state.user.attributes.sub);
    },
    carPhotoUrl: function() {
      if (!this.car.photoId) {
        return '';
      }
      return url.resolve(aws_exports.mediaBucketUrl, `car-photos/${this.car.photoId}`);
    },
    carAudioUrl: function() {
      if (!this.car.audioId) {
        return '';
      }
      return url.resolve(aws_exports.mediaBucketUrl, `car-audio/${this.car.audioId}`)
    },
    loaderText: function() {
      return (this.carNotFound) ? 'Car not found' : 'Loading car data';
    }
  },
  methods: {
    loadCarFromLinkIfNeeded() {
      if (this.$route.params.pathMatch) {
        this.carId = this.$route.params.pathMatch;
        this.loading = true;
        this.fetchCar(this.carId);
      }
    },
    save() {
      this.setStatus("", "");
      if (this.carId) {
        API.put("carUpload", `/${this.carId}`, { body: this.getCarForm() })
          .then(response => {
            console.log(response);
            this.setStatus("success", "Car updated successfully");
          })
          .catch(error => {
            this.setStatus("error", error.response.data.message);
          });
      } else {
        API.post("carUpload", "", { body: this.getCarForm() })
          .then(response => {
            console.log(response);
            this.$router.push(this.$route.path + response.id);
          })
          .catch(error => {
            let errorMsg = (error.response) ? error.response.data.message : 'Error during car save operation';
            this.setStatus('error', errorMsg);
          });
      }
    },
    getCarForm: function() {
      return {
        carTitle: this.car.title,
        carDescription: this.car.description,
        engine: this.car.engine,
        horsePower: parseInt(this.car.horsePower),
        mileage: parseInt(this.car.mileage),
        year: parseInt(this.car.productionYear),
        photoId: this.car.photoId,
        audioId: this.car.audioId
      };
    },
    deleteCar: async function() {
      API.del('carUpload', `/${this.carId}`, { body: {} })
        .then(response => {
          console.log(response);
          this.$router.replace('/');
        })
        .catch(error => {
          console.log(error);
          if (error.response) {
            this.setStatus('error', error.response.data.message);
          }
          else {
            this.setStatus('error', 'Unexpected error during delete operation');
          }
        })
      // TODO
    },
    loadCar(car) {
      this.car.title = car.carTitle,
      this.car.description = car.carDescription;
      this.car.engine = car.engine;
      this.car.horsePower = car.horsePower;
      this.car.mileage = car.mileage;
      this.car.productionYear = car.year;
      this.car.photoId = car.photoId;
      this.car.audioId = car.audioId;
      this.car.ownerId = car.owner.id;
      this.car.ownerName = car.owner.name;
    },
    fetchCar(carId) {
      return API.get("carFetch", "/" + carId)
        .then(response => {
          console.log('Fetched car: ', response);
          this.loading = false;
          this.loadCar(response);
        })
        .catch(error => {
          console.log('Car fetch error: ', error);
          if (error.response) {
            if (error.response.status === 404) {
              this.carNotFound = true;
            }
            else {
              this.setStatus('error', error.response.data.message);
            }
          }
          else {
            this.setStatus('error', 'Failed to fetch car information');
          }
        });
    },
    setStatus: async function(status, message) {
      this.statusInfo = {
        status: status,
        message: message
      };
      this.$el.querySelector('.car-details-status-message')
    },
    onPhotoUploadError: function(event) {
      this.setStatus('error', event.message);
    },
    onAudioUploadError: function(event) {
      this.setStatus('error', event.message);
    }
  },
  components: {
    PhotosUpload,
    AudioUpload,
    AudioPlayer,
    StatusMessage
  }
};
</script>

<style scoped lang="scss">
#car-details-container {
  .car-details-status-message {
    width: 100%;
  }

  .car-loading-screen {
    color: darkgray;
    padding: 3em;
  }

  .car-details {
    display: flex;
    flex-direction: column;
    align-items: center;

    padding: 2em;

    .car-photo {
      width: 50%;
    }

    .car-input {
      width: 50%;
      padding: 1em;

      label {
        align-self: flex-start;
        font-weight: bold;
      }
    }

    .car-photo-input, .car-audio-input {
      display: flex;
      flex-direction: column;
      align-items: center;

      label {
        align-self: center;
      }
    }

    .car-audio-player {
      display: flex;
      justify-content: center;
    }

    .car-text-input {
      display: flex;
      flex-direction: column;
    }

    .car-value-input {
      display: flex;
      align-items: center;

      label {
        flex: 3;
        align-self: center;
        margin-right: 2em;
        text-align: end;
      }

      input {
        flex: 3;
        text-align: center;
      }

      span {
        flex: 6;
        text-align: start;
        padding-left: 1em;
      }

      .value-measure {
        font-style: italic;
      }
    }

    .car-engine-input {
      label {
        flex: 3;
      }

      input {
        flex: 9;
        text-align: start;
      }
    }
  }

  .car-edit-buttons {
    display: flex;
    justify-content: center;
    margin-bottom: 2em;

    #saveButton {
      margin: 1em;
      font-weight: bold;
    }

    #deleteButton {
      background-color: red;
      font-weight: bold;
      margin: 1em;
    }
  }

  .car-do-edit {
    margin: 1em;
  }
}
</style>