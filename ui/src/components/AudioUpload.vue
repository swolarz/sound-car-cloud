<template>
  <div class="audio-upload">
    <b-icon-soundwave class="h2" />
    <input type="file" accept="audio/*" @change="onFileSelected" />
    <button @click="onUploadButtonClicked">Upload</button>
  </div>
</template>

<script>
import { API } from "aws-amplify";

export default {
  name: "AudioUpload",
  props: {
    value: String
  },
  data: function() {
    return {
      selectedFile: null,
      lastAudioId: null
    };
  },
  methods: {
    onFileSelected(event) {
      this.selectedFile = event.target.files[0];
    },
    onUploadButtonClicked() {
      if (!this.selectedFile) {
        return;
      }
      const audioExtension = this.selectedFile.name.split('.').pop();
      if (!(['wav', 'mp3'].includes(audioExtension))) {
        this.$emit('uploaderror', { message: 'Only .wav and .mp3 audio files are supported' });
        return;
      }

      const reader = new FileReader();
      reader.onload = e => this.sendAudio(e.target.result);
      reader.readAsDataURL(this.selectedFile);
    },
    sendAudio(audioContents) {
      let params = {
        body: {
          audio: audioContents,
          prevAudioId: this.lastAudioId
        }
      };

      API.post("carAudioUpload", "", params)
        .then(response => {
          this.lastAudioId = response.audioId;
          console.log(response);

          this.$emit("input", response.audioId);
        })
        .catch(error => {
          this.$emit('uploaderror', { message: error.message });
        });
    }
  }
};
</script>

<style scoped lang="scss">
.audio-upload {
  display: flex;
  align-items: center;
}
</style>