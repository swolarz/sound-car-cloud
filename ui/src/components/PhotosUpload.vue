<template>
    <div class="photos-upload">
        <b-icon-camera class="h2" />
        <input type="file" accept="image/*" @change="onFileSelected" />
        <button @click="onUploadButtonClicked">Upload</button>
    </div>
</template>

<script>
import { API } from "aws-amplify";

export default {
    name: 'PhotosUploader',
    props: {
        value: String
    },
    data() {
        return {
            selectedFile: null,
            lastPhotoId: null
        }
    },
    methods: {
        onFileSelected(event) {
            this.selectedFile = event.target.files[0];
        },
        onUploadButtonClicked() {
            if (!this.selectedFile) {
                return;
            }
            const reader = new FileReader();
            reader.onload = e => this.sendImage(e.target.result);
            reader.readAsDataURL(this.selectedFile);
        },
        sendImage(imageContents) {
            let params = {
                body: {
                    photo: imageContents,
                    prevPhotoId: this.lastPhotoId
                }
            }

            API.post("carPhotosUpload", "", params)
                .then(response => {
                    console.log(response);
                    this.lastPhotoId = response.photoId;
                    this.$emit('input', response.photoId);
                })
                .catch(error => {
                    this.$emit('uploaderror', { message: error.message });
                });
        }
    }
}
</script>

<style scoped lang="scss">
.photos-upload {
    display: flex;
    align-items: center;
}
</style>