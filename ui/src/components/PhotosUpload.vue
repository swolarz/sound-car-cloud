<template>
  <div class="photosUploader">
    <input type="file" @change="onFileSelected">
    <button @click="onUploadButtonClicked">Upload</button>
  </div>
</template>

<script>
import { API } from "aws-amplify";

export default {
  name: 'PhotosUploader',
  props: {
    carId: String,
  },
  data() {
      return {
          selectedFile: null
      }
  },
  methods: {
      onFileSelected(event) {
          this.selectedFile = event.target.files[0];
          console.log(this.carId);
      },
      onUploadButtonClicked() {
          readBytesOfFile(this.selectedFile, this.sendFile);
      },
      sendFile(file) {
        let params = {
            body: {
                photo: file,
                carId: this.carId
            }
        }

        API.post("uploadPhotos", "", params)
        .then(response => {
            console.log(response);
        })
        .catch(error => {
            console.log(error);
        });
      }
  }
}

function readBytesOfFile(file, callback) {
    const reader = new FileReader();
    reader.onload = e => callback(e.target.result);
    reader.readAsDataURL(file);
}

</script>