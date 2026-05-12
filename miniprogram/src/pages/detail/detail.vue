<template>
  <view class="container">
    <!-- Top Image Banner -->
    <view class="banner-section">
      <image class="banner-img" :src="venue.cover || 'https://images.unsplash.com/photo-1545128485-c400e7702796?w=750&auto=format&fit=crop&q=80'" mode="aspectFill"></image>
      <view class="image-count">
        <text class="count-text">1张</text>
      </view>
    </view>

    <!-- Header Information Block -->
    <view class="detail-header">
      <view class="top-info">
        <view class="title-row">
          <text class="venue-name">{{ venue.name || '加载中...' }}</text>
          <text class="emoji-icons">🔴 🔥 🐉</text>
        </view>
        <view :class="['status-tag', venue.open_status ? 'status-open' : 'status-closed']">
          {{ venue.open_status ? '今日营业' : '今日停业' }}
        </view>
      </view>

      <!-- Detailed Info Items -->
      <view class="info-list">
        <view class="info-item" @click="openLocation">
          <text class="info-icon">📍</text>
          <view class="info-content">
            <text class="info-text">{{ venue.province || '' }}{{ venue.city || '' }}{{ venue.address || '地址未知' }}</text>
            <text class="info-subtext">直线距离 {{ venue.distance_display || '未知' }} · 点击可导航</text>
          </view>
          <text class="arrow">➔</text>
        </view>

        <view class="info-item">
          <text class="info-icon">🕒</text>
          <view class="info-content">
            <text class="info-text">午场: {{ venue.afternoon_hours || '暂无' }}</text>
            <text class="info-text">晚场: {{ venue.evening_hours || '暂无' }}</text>
          </view>
        </view>

        <view class="info-item">
          <text class="info-icon">🎟️</text>
          <view class="info-content">
            <text class="info-text">{{ venue.ticket_price || '暂无门票价格信息' }}</text>
          </view>
        </view>

        <view class="info-item">
          <text class="info-icon">💬</text>
          <view class="info-content">
            <text class="info-text highlight-blue" @click="goToClaim">推荐舞厅工作人员认领舞厅添加联系方式</text>
          </view>
        </view>
      </view>
    </view>

    <!-- Content Block -->
    <view class="content-section">
      <view class="detail-tab-content">
        <text class="detail-line">@所有人 {{ venue.city || '未知' }}：{{ venue.name || '舞厅' }}</text>
        <text class="detail-line">营业时间：{{ venue.open_status ? '正常营业中' : '休息中' }}</text>
        <text class="detail-line" v-if="venue.afternoon_hours">午场：{{ venue.afternoon_hours }}</text>
        <text class="detail-line" v-if="venue.evening_hours">晚场：{{ venue.evening_hours }}</text>
        <text class="detail-line">导航：{{ venue.name || '舞厅' }}</text>
        <text class="detail-line">地址：{{ venue.province || '' }}{{ venue.city || '' }}{{ venue.address || '' }}</text>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref } from 'vue';
import { onLoad } from '@dcloudio/uni-app';
import { request } from '@/request.js'

const venue = ref({});

onLoad((options) => {
  const id = options.id;
  if (id) {
    request({
      url: `/api/dance-halls/${id}`,
      data: {
        latitude: 30.6586,
        longitude: 104.0648
      },
      success: (res) => {
        if(res.data && res.data.code === 200) {
          venue.value = res.data.data;
        } else {
          uni.showToast({ title: '加载失败', icon: 'none' });
        }
      }
    });
  }
});

const goToClaim = () => {
  uni.navigateTo({ url: '/pages/claim/claim' });
};

const openLocation = () => {
  if (venue.value.latitude && venue.value.longitude) {
    uni.openLocation({
      latitude: parseFloat(venue.value.latitude),
      longitude: parseFloat(venue.value.longitude),
      name: venue.value.name,
      address: venue.value.address
    });
  } else {
    uni.showToast({ title: '暂无经纬度信息', icon: 'none' });
  }
};
</script>

<style>
page {
  background-color: #ffffff;
  color: #111827;
}
.container {
  padding-bottom: 60rpx;
  position: relative;
}

/* Banner Section */
.banner-section {
  width: 100%;
  height: 420rpx;
  position: relative;
  background-color: #f3f4f6;
}
.banner-img {
  width: 100%;
  height: 100%;
}
.image-count {
  position: absolute;
  bottom: 24rpx;
  right: 24rpx;
  background: rgba(0, 0, 0, 0.6);
  border-radius: 30rpx;
  padding: 6rpx 20rpx;
}
.count-text {
  color: #ffffff;
  font-size: 22rpx;
  font-weight: bold;
}

/* Header Information Block */
.detail-header {
  background: #ffffff;
  border-radius: 24rpx;
  padding: 32rpx;
  margin: -32rpx 24rpx 24rpx;
  border: 1px solid #e5e7eb;
  position: relative;
  z-index: 10;
}
.top-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24rpx;
}
.title-row {
  display: flex;
  align-items: center;
}
.venue-name {
  font-size: 40rpx;
  font-weight: bold;
  color: #111827;
  margin-right: 12rpx;
}
.emoji-icons {
  font-size: 28rpx;
}
.status-tag {
  padding: 6rpx 20rpx;
  border-radius: 30rpx;
  font-size: 22rpx;
  font-weight: bold;
}
.status-open {
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
  border: 1px solid rgba(16, 185, 129, 0.2);
}
.status-closed {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
  border: 1px solid rgba(239, 68, 68, 0.2);
}

.info-list {
  display: flex;
  flex-direction: column;
}
.info-item {
  display: flex;
  align-items: flex-start;
  padding: 18rpx 0;
  border-bottom: 1px solid #f3f4f6;
}
.info-item:last-child {
  border-bottom: none;
}
.info-icon {
  font-size: 32rpx;
  margin-right: 20rpx;
  padding-top: 2rpx;
}
.info-content {
  flex: 1;
}
.info-text {
  font-size: 26rpx;
  color: #1f2937;
  line-height: 1.5;
  display: block;
}
.info-subtext {
  font-size: 22rpx;
  color: #6b7280;
  margin-top: 4rpx;
  display: block;
}
.highlight-blue {
  color: #2563eb;
  text-decoration: underline;
}
.arrow {
  color: #9ca3af;
  font-size: 26rpx;
  margin-left: 12rpx;
  align-self: center;
}

/* Content Section */
.content-section {
  background: #ffffff;
  margin: 0 24rpx 32rpx;
  border-radius: 20rpx;
  padding: 36rpx;
  border: 1px solid #e5e7eb;
  min-height: 300rpx;
}
.detail-tab-content {
  display: flex;
  flex-direction: column;
}
.detail-line {
  font-size: 28rpx;
  color: #374151;
  line-height: 1.8;
}
</style>
