<template>
  <div v-if="audioUrl" class="sound-player">
    <b-icon-music-player class="h2" />
    <b-icon-play-fill class="h2" v-if="!playing" @click="playAudio" />
    <b-icon-pause-fill class="h2" v-if="playing" @click="pauseAudio" />
    <b-icon-stop-fill class="h2" v-if="audioPlayer != null" @click="stopAudio" />
  </div>
</template>

<script>
export default {
  name: 'AudioPlayer',
  props: {
    audioUrl: String
  },
  data: function() {
    return {
      audioPlayer: null,
      playerOrder: 0,
      playing: false
    }
  },
  beforeDestroy: function() {
    this.ensureAudioStopped();
    
  },
  watch: {
    '$store.state.audio.orderIndex': function() {
      if (this.playerOrder < this.$store.state.audio.orderIndex) {
        this.ensureAudioPaused();
      }
    }
  },
  computed: {
    paused: function() {
      return (!this.playing && this.audioPlayer !== null);
    }
  },
  methods: {
    playAudio: async function() {
      if (!this.paused) {
        this.audioPlayer = new Audio(this.audioUrl);
        this.audioPlayer.addEventListener('ended', () => {
          this.ensureAudioStopped();
        });
      }

      this.playerOrder += 1;
      this.$store.state.audio.orderIndex = this.playerOrder;

      this.playing = true;
      this.audioPlayer.play();
    },
    pauseAudio: async function() {
      this.ensureAudioPaused();
    },
    stopAudio: async function() {
      this.ensureAudioStopped();
    },
    ensureAudioPaused: function() {
      if (this.audioPlayer === null) {
        return;
      }
      this.audioPlayer.pause();
      this.playing = false;
    },
    ensureAudioStopped: function() {
      if (this.audioPlayer === null) {
        return;
      }
      this.audioPlayer.pause();
      this.audioPlayer = null;
      this.playing = false;
    }
  }
}
</script>

<style scoped lang="scss">
.sound-player {
  display: flex;
  align-items: center;
}
</style>