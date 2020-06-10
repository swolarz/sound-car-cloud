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
  data() {
      return {
          selectedFile: null
      }
  },
  methods: {
      onFileSelected(event) {
          this.selectedFile = event.target.files[0];
      },
      onUploadButtonClicked() {
          getBase64(this.selectedFile, this.sendFile);
      },
      sendFile(file) {
        let params = {
            body: {
                photo: file
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

function getBase64(file, callback) {
   var reader = new FileReader();
   reader.readAsDataURL(file);
   reader.onload = function () {
     callback(reader.result);
   };
   reader.onerror = function (error) {
     console.log('Error: ', error);
   };
}
</script>