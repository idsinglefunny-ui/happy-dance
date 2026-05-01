<template>
  <view class="container">
    <view class="config-card">
      <view class="config-row picker-row">
        <text class="label">计费模式：</text>
        <picker :range="modes" :value="modeIndex" @change="onModeChange" class="picker-box">
          <view class="picker-text">{{ modes[modeIndex] }}</view>
        </picker>
      </view>
    </view>

    <view class="config-card">
      <view class="input-group">
        <text class="input-label">每曲时长 (分钟，支持输入小数点)：</text>
        <input class="input" type="digit" v-model="songDuration" />
      </view>
      <view class="input-group" style="margin-top: 30rpx;">
        <text class="input-label">每曲费用 (元)：</text>
        <input class="input" type="digit" v-model="songCost" />
      </view>
    </view>

    <view class="action-row">
      <button v-if="!isRunning && !isEnded" class="btn btn-start" @click="startTimer">
        💃 开始计时
      </button>
      <button v-if="isRunning" class="btn btn-start" @click="addManualSong">
        💃 重新开始
      </button>
      <button class="btn btn-end" @click="endTimer" :disabled="!isRunning && !isEnded">
        ⏹ 结束计时
      </button>
      <button class="btn btn-reset" @click="resetTimer">
        🔄 重新计算
      </button>
    </view>

    <view class="status-text" v-if="isRunning || isEnded">
      <text>开始时间：{{ formatTime(startTime) }}</text>
      <text v-if="isRunning">已用时：{{ formatDuration(elapsedMs) }}</text>
    </view>

    <view class="result-card" v-if="isRunning || isEnded">
      <view class="summary-row">
        <view class="summary-box">
          <text class="summary-title">总费用</text>
          <text class="summary-value highlight">{{ totalCost }} 元</text>
        </view>
        <view class="summary-box">
          <text class="summary-title">已跳曲数</text>
          <text class="summary-value highlight">{{ songsCount }} 首</text>
        </view>
      </view>

      <view class="detail-list">
        <view class="detail-row">
          <text class="detail-label">开始时间：</text>
          <text class="detail-val">{{ formatTime(startTime) }}</text>
        </view>
        <view class="detail-row">
          <text class="detail-label">结束时间：</text>
          <text class="detail-val">{{ isEnded ? formatTime(endTime) : '--:--:--' }}</text>
        </view>
        <view class="detail-row">
          <text class="detail-label">持续时长：</text>
          <text class="detail-val">{{ formatDuration(elapsedMs) }}</text>
        </view>
        
        <view class="divider"></view>
        
        <text class="detail-title">费用明细：</text>
        <view class="song-item" v-for="(song, index) in songRecords" :key="index">
          <view class="song-header">
            <text class="song-name">第{{ index + 1 }}首</text>
            <text class="song-price">{{ song.cost }}元</text>
          </view>
          <view class="song-time">
            {{ formatTime(song.start) }} ~ {{ song.end ? formatTime(song.end) : '--:--:--' }} 
            <text class="song-duration">({{ Math.floor(song.duration / 1000) }}秒)</text>
          </view>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref, computed, onUnmounted } from 'vue';

const modes = ['连曲模式', '非连曲', '按分钟计费'];
const modeIndex = ref(1); // Default to 非连曲
const songDuration = ref('2.5');
const songCost = ref('20');

const isRunning = ref(false);
const isEnded = ref(false);
const startTime = ref(null);
const endTime = ref(null);
const elapsedMs = ref(0);

const songRecords = ref([]);
let timerInterval = null;

const onModeChange = (e) => {
  modeIndex.value = e.detail.value;
};

const formatTime = (dateObj) => {
  if (!dateObj) return '';
  const d = new Date(dateObj);
  return `${d.getHours().toString().padStart(2, '0')}:${d.getMinutes().toString().padStart(2, '0')}:${d.getSeconds().toString().padStart(2, '0')}`;
};

const formatDuration = (ms) => {
  const totalSecs = Math.floor(ms / 1000);
  const h = Math.floor(totalSecs / 3600).toString().padStart(2, '0');
  const m = Math.floor((totalSecs % 3600) / 60).toString().padStart(2, '0');
  const s = (totalSecs % 60).toString().padStart(2, '0');
  return `${h}:${m}:${s}`;
};

const calcSongsAndCost = () => {
  let count = songRecords.value.length;
  if (count === 0 && isRunning.value) count = 1;
  return {
    count,
    cost: count * parseFloat(songCost.value || 0)
  };
};

const songsCount = computed(() => calcSongsAndCost().count);
const totalCost = computed(() => calcSongsAndCost().cost);

const startTimer = () => {
  isRunning.value = true;
  isEnded.value = false;
  const now = Date.now();
  startTime.value = now;
  elapsedMs.value = 0;
  
  // Create first song record
  songRecords.value = [{
    start: now,
    end: null,
    duration: 0,
    cost: parseFloat(songCost.value || 0)
  }];
  
  timerInterval = setInterval(() => {
    const current = Date.now();
    elapsedMs.value = current - startTime.value;
    
    // Update current song duration
    const currentSong = songRecords.value[songRecords.value.length - 1];
    if (currentSong) {
      currentSong.duration = current - currentSong.start;
    }
    
    // 如果是连曲模式，自动判断是否超过时长，超过则自动切歌计费
    if (modeIndex.value === 0) {
      const limitMs = parseFloat(songDuration.value) * 60 * 1000;
      if (currentSong.duration >= limitMs) {
        currentSong.end = current;
        songRecords.value.push({
          start: current,
          end: null,
          duration: 0,
          cost: parseFloat(songCost.value || 0)
        });
      }
    }
  }, 1000);
};

const addManualSong = () => {
  // 手动点击重新开始，结算当前歌曲，新开一首
  const now = Date.now();
  const currentSong = songRecords.value[songRecords.value.length - 1];
  if (currentSong) {
    currentSong.end = now;
    currentSong.duration = now - currentSong.start;
  }
  songRecords.value.push({
    start: now,
    end: null,
    duration: 0,
    cost: parseFloat(songCost.value || 0)
  });
};

const endTimer = () => {
  if (!isRunning.value) return;
  isRunning.value = false;
  isEnded.value = true;
  clearInterval(timerInterval);
  endTime.value = Date.now();
  
  const currentSong = songRecords.value[songRecords.value.length - 1];
  if (currentSong) {
    currentSong.end = endTime.value;
    currentSong.duration = endTime.value - currentSong.start;
  }
};

const resetTimer = () => {
  isRunning.value = false;
  isEnded.value = false;
  clearInterval(timerInterval);
  startTime.value = null;
  endTime.value = null;
  elapsedMs.value = 0;
  songRecords.value = [];
};

onUnmounted(() => {
  if (timerInterval) clearInterval(timerInterval);
});
</script>

<style>
page {
  background-color: #0b0b0e;
  color: #ffffff;
}
.container {
  padding: 24rpx;
  padding-bottom: 60rpx;
}
.config-card {
  background: #15151e;
  border-radius: 16rpx;
  padding: 30rpx;
  margin-bottom: 24rpx;
}
.config-row {
  display: flex;
  align-items: center;
}
.label {
  font-size: 28rpx;
  color: #dddddd;
}
.picker-box {
  background: #1e1e28;
  padding: 10rpx 30rpx;
  border-radius: 8rpx;
  margin-left: 20rpx;
}
.picker-text {
  font-size: 28rpx;
  color: #ffffff;
}
.input-group {
  display: flex;
  flex-direction: column;
}
.input-label {
  font-size: 26rpx;
  color: #aaaaaa;
  margin-bottom: 16rpx;
}
.input {
  background: #1e1e28;
  height: 80rpx;
  border-radius: 8rpx;
  padding: 0 20rpx;
  color: #ffffff;
  font-size: 32rpx;
  border: 1px solid #2a2a36;
}
.action-row {
  display: flex;
  justify-content: space-between;
  margin: 40rpx 0;
}
.btn {
  flex: 1;
  margin: 0 10rpx;
  height: 90rpx;
  border-radius: 12rpx;
  font-size: 28rpx;
  font-weight: bold;
  display: flex;
  align-items: center;
  justify-content: center;
  border: none;
  color: #ffffff;
}
.btn-start { background: linear-gradient(135deg, #b040ff, #e5007f); }
.btn-end { background: linear-gradient(135deg, #00b4db, #0083b0); }
.btn-reset { background: linear-gradient(135deg, #a800ff, #6a00ff); }

.status-text {
  display: flex;
  justify-content: space-between;
  font-size: 24rpx;
  color: #888888;
  margin-bottom: 20rpx;
  padding: 0 10rpx;
}

.result-card {
  background: #15151e;
  border-radius: 16rpx;
  padding: 30rpx;
}
.summary-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 40rpx;
}
.summary-box {
  flex: 1;
  background: #1e1e28;
  margin: 0 10rpx;
  padding: 30rpx 0;
  border-radius: 12rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
}
.summary-title {
  font-size: 26rpx;
  color: #888888;
  margin-bottom: 10rpx;
}
.summary-value {
  font-size: 40rpx;
  font-weight: bold;
}
.highlight {
  color: #b040ff;
}

.detail-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 16rpx;
  font-size: 26rpx;
}
.detail-label { color: #888888; }
.detail-val { color: #dddddd; }

.divider {
  height: 1px;
  background: #2a2a36;
  margin: 30rpx 0;
}
.detail-title {
  font-size: 28rpx;
  font-weight: bold;
  color: #ffffff;
  display: block;
  margin-bottom: 20rpx;
}
.song-item {
  margin-bottom: 20rpx;
}
.song-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 10rpx;
}
.song-name { font-size: 26rpx; font-weight: bold; }
.song-price { font-size: 26rpx; color: #b040ff; font-weight: bold; }
.song-time { font-size: 24rpx; color: #888888; }
.song-duration { color: #555555; margin-left: 10rpx; }
</style>
