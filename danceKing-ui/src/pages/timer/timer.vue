<template>
  <view class="container">
    <view class="timer-display">
      <text class="time-text">{{ formattedTime }}</text>
      <text class="ms-text">.{{ formattedMs }}</text>
    </view>
    
    <view class="controls">
      <button class="btn btn-reset" @click="resetTimer">重置</button>
      <button class="btn btn-main" @click="toggleTimer">
        {{ isRunning ? '暂停' : '开始' }}
      </button>
    </view>

    <view class="tips">
      <text>专为舞蹈练习与轮转打卡设计</text>
    </view>
  </view>
</template>

<script setup>
import { ref, computed, onUnmounted } from 'vue';

const timeMs = ref(0);
const isRunning = ref(false);
let interval = null;

const toggleTimer = () => {
  if (isRunning.value) {
    clearInterval(interval);
    isRunning.value = false;
  } else {
    isRunning.value = true;
    const startTime = Date.now() - timeMs.value;
    interval = setInterval(() => {
      timeMs.value = Date.now() - startTime;
    }, 10);
  }
};

const resetTimer = () => {
  clearInterval(interval);
  isRunning.value = false;
  timeMs.value = 0;
};

const formattedTime = computed(() => {
  const totalSeconds = Math.floor(timeMs.value / 1000);
  const minutes = Math.floor(totalSeconds / 60).toString().padStart(2, '0');
  const seconds = (totalSeconds % 60).toString().padStart(2, '0');
  return `${minutes}:${seconds}`;
});

const formattedMs = computed(() => {
  return Math.floor((timeMs.value % 1000) / 10).toString().padStart(2, '0');
});

onUnmounted(() => {
  if (interval) clearInterval(interval);
});
</script>

<style>
page {
  background-color: #0b0b0e;
  color: #ffffff;
  height: 100%;
}
.container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 80vh;
}
.timer-display {
  display: flex;
  align-items: baseline;
  justify-content: center;
  background: #15151e;
  padding: 60rpx 40rpx;
  border-radius: 40rpx;
  border: 2px solid #2a2a36;
  box-shadow: 0 0 40rpx rgba(229, 0, 127, 0.2);
  margin-bottom: 100rpx;
  width: 500rpx;
}
.time-text {
  font-size: 160rpx;
  font-weight: bold;
  color: #e5007f;
  text-shadow: 0 0 20rpx rgba(229, 0, 127, 0.5);
  font-variant-numeric: tabular-nums;
}
.ms-text {
  font-size: 60rpx;
  color: #e5007f;
  font-weight: bold;
  margin-left: 10rpx;
  font-variant-numeric: tabular-nums;
}
.controls {
  display: flex;
  justify-content: center;
  width: 100%;
  gap: 40rpx;
}
.btn {
  border-radius: 60rpx;
  font-size: 36rpx;
  font-weight: bold;
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100rpx;
  width: 240rpx;
}
.btn-reset {
  background: #2a2a36;
  color: #ffffff;
}
.btn-main {
  background: linear-gradient(90deg, #e5007f, #9900ff);
  color: #ffffff;
  box-shadow: 0 10rpx 20rpx rgba(229, 0, 127, 0.3);
}
.tips {
  margin-top: 100rpx;
  font-size: 24rpx;
  color: #555555;
}
</style>
