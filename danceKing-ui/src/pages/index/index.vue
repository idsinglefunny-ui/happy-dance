<template>
  <view class="container">
    <!-- Top Banner -->
    <view class="banner">
      <image class="banner-img" src="https://via.placeholder.com/750x300/1a1a24/e5007f?text=YOUR+BANNER+AD" mode="aspectFill"></image>
    </view>

    <!-- Quick Navigation -->
    <view class="nav-grid">
      <view class="nav-item">
        <text class="nav-icon">🌍</text>
        <text class="nav-text">全国舞讯</text>
      </view>
      <view class="nav-item" @click="goToClaim">
        <text class="nav-icon">✨</text>
        <text class="nav-text">认领舞厅</text>
      </view>
      <view class="nav-item" @click="goToTimer">
        <text class="nav-icon">⏱️</text>
        <text class="nav-text">专属计时</text>
      </view>
      <button class="nav-item contact-btn" open-type="contact">
        <text class="nav-icon">💬</text>
        <text class="nav-text">在线客服</text>
      </button>
    </view>

    <!-- Filter -->
    <view class="filter-section">
      <view class="filter-btn active">全部</view>
      <view class="filter-btn">今日营业</view>
      <view class="filter-btn">今日停业</view>
    </view>

    <!-- Venue List -->
    <view class="venue-list">
      <view class="venue-card" v-for="(venue, index) in venues" :key="index">
        <view class="card-header">
          <text class="venue-name">{{ venue.name }}</text>
          <view :class="['status-tag', venue.open_status ? 'status-open' : 'status-closed']">
            {{ venue.open_status ? 'OPEN NOW' : 'CLOSED' }}
          </view>
        </view>
        
        <view class="card-body">
          <text class="venue-hours">{{ venue.afternoon_hours }} / {{ venue.evening_hours }}</text>
          <text class="venue-notice" v-if="venue.moment_text">{{ venue.moment_text }}</text>
        </view>
        
        <view class="card-footer">
          <text class="venue-address">{{ venue.city }} · {{ venue.address }}</text>
          <view class="distance-box">
            <text class="distance-text">{{ venue.distance_display || '计算中' }}</text>
            <text class="nav-arrow">➔</text>
          </view>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref, onMounted } from 'vue';

const venues = ref([]);

const fetchVenues = () => {
  // 模拟请求，真实环境中使用 uni.getLocation 获取经纬度
  uni.request({
    url: 'http://localhost:8000/api/dance-halls',
    data: { latitude: 30.6586, longitude: 104.0648 },
    success: (res) => {
      if(res.data && res.data.code === 200) {
        venues.value = res.data.data;
      }
    }
  });
};

const goToClaim = () => {
  uni.navigateTo({ url: '/pages/claim/claim' });
};

const goToTimer = () => {
  uni.navigateTo({ url: '/pages/timer/timer' });
};

onMounted(() => {
  fetchVenues();
});
</script>

<style>
page {
  background-color: #0b0b0e;
  color: #ffffff;
}
.container {
  padding-bottom: 40rpx;
}
.banner {
  width: 100%;
  height: 300rpx;
  background: #1a1a24;
}
.banner-img {
  width: 100%;
  height: 100%;
}
.nav-grid {
  display: flex;
  justify-content: space-around;
  padding: 30rpx 0;
  background-color: #111118;
  margin-bottom: 20rpx;
}
.nav-item {
  display: flex;
  flex-direction: column;
  align-items: center;
}
.contact-btn {
  background: transparent;
  padding: 0;
  margin: 0;
  line-height: inherit;
  border: none;
}
.contact-btn::after {
  display: none;
}
.nav-icon {
  font-size: 50rpx;
  margin-bottom: 10rpx;
}
.nav-text {
  font-size: 24rpx;
  color: #aaaaaa;
}
.filter-section {
  display: flex;
  padding: 0 24rpx;
  margin-bottom: 20rpx;
}
.filter-btn {
  padding: 10rpx 30rpx;
  border-radius: 30rpx;
  background: #1a1a24;
  color: #888;
  font-size: 26rpx;
  margin-right: 20rpx;
}
.filter-btn.active {
  background: #e5007f;
  color: #fff;
  box-shadow: 0 0 10rpx rgba(229, 0, 127, 0.5);
}
.venue-list {
  padding: 0 24rpx;
}
.venue-card {
  background: #15151e;
  border-radius: 20rpx;
  padding: 30rpx;
  margin-bottom: 30rpx;
  border: 1px solid #2a2a36;
  position: relative;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20rpx;
}
.venue-name {
  font-size: 36rpx;
  font-weight: bold;
  color: #ffffff;
}
.status-tag {
  padding: 4rpx 16rpx;
  border-radius: 8rpx;
  font-size: 22rpx;
  font-weight: bold;
}
.status-open {
  background: rgba(0, 255, 128, 0.1);
  color: #00ff80;
  border: 1px solid #00ff80;
  box-shadow: 0 0 8rpx rgba(0, 255, 128, 0.3);
}
.status-closed {
  background: rgba(255, 64, 64, 0.1);
  color: #ff4040;
  border: 1px solid #ff4040;
}
.card-body {
  margin-bottom: 20rpx;
}
.venue-hours {
  font-size: 26rpx;
  color: #bbbbbb;
  display: block;
}
.venue-notice {
  display: inline-block;
  margin-top: 10rpx;
  font-size: 24rpx;
  color: #e5007f;
  background: rgba(229, 0, 127, 0.1);
  padding: 4rpx 12rpx;
  border-radius: 4rpx;
}
.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
}
.venue-address {
  font-size: 24rpx;
  color: #777777;
  max-width: 70%;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.distance-box {
  display: flex;
  align-items: center;
  background: #e5007f;
  padding: 8rpx 20rpx;
  border-radius: 12rpx;
  box-shadow: 0 0 10rpx rgba(229, 0, 127, 0.4);
}
.distance-text {
  font-size: 26rpx;
  font-weight: bold;
  color: #ffffff;
  margin-right: 10rpx;
}
.nav-arrow {
  font-size: 24rpx;
  color: #ffffff;
}
</style>
