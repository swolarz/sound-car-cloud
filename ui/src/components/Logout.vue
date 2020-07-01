<template>
  <div></div>
</template>

<script>
import { Auth } from 'aws-amplify';

export default {
    name: 'Logout',
    created: function() {
      Auth.signOut()
        .then(data => {
          this.$store.state.signedIn = !!data;
          this.$router.replace('/');
        })
        .catch(() => {
          this.$router.replace('/');
        });
    }
}
</script>