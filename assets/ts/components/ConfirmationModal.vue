<template>
  <div
    class="modal fade"
    :class="{ show: modalOpen, 'd-block': modalOpen }"
    tabindex="-1"
    role="dialog"
  >
    <div class="modal-dialog">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">Are you sure?</h5>
        </div>
        <div class="modal-body">
          <p>This operation can't be undone!</p>
        </div>
        <div class="modal-footer">
          <button
            type="button"
            class="btn btn-danger"
            @click="$emit('click-yes')"
          >
            Yes, I'm sure
          </button>
          <button
            type="button"
            class="btn btn-secondary"
            @click="$emit('click-no')"
          >
            No
          </button>
        </div>
      </div>
    </div>
  </div>
  <div v-if="modalOpen" class="modal-backdrop fade show"></div>
</template>

<script lang="ts">
import { defineComponent } from "vue";

export default defineComponent({
  name: "ConfirmationModal",
  props: {
    modalOpen: {
      type: Boolean,
      default: false,
    },
  },
  emits: ["click-yes", "click-no"],
});
</script>
