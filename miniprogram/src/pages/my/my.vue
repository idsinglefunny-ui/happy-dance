<template>
  <view class="container">
    <view class="user-info">
      <view class="avatar">👤</view>
      <text class="nickname">微信用户</text>
    </view>
    
    <view class="menu-list">
      <view class="menu-item" @click="goToClaim">
        <text>认领舞厅 / 商家入口</text>
        <text class="arrow">➔</text>
      </view>
      <button class="menu-item contact-btn" open-type="contact">
        <text>联系平台客服</text>
        <text class="arrow">➔</text>
      </button>
    </view>
  </view>
</template>

<script setup>
const goToClaim = () => {
  uni.navigateTo({ url: '/pages/claim/claim' });
};
</script>

<style>
page {
  background-color: #ffffff;
  color: #111827;
}
.container {
  padding: 24rpx;
}
.user-info {
  display: flex;
  align-items: center;
  margin-bottom: 32rpx;
  padding: 48rpx 32rpx;
  background: #ffffff;
  border-radius: 20rpx;
  border: 1px solid #e5e7eb;
}
.avatar {
  width: 120rpx;
  height: 120rpx;
  background: #f3f4f6;
  border: 1px solid #e5e7eb;
  border-radius: 60rpx;
  margin-right: 32rpx;
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 56rpx;
}
.nickname {
  font-size: 36rpx;
  font-weight: bold;
  color: #111827;
}
.menu-list {
  background: #ffffff;
  border-radius: 20rpx;
  border: 1px solid #e5e7eb;
  overflow: hidden;
}
.menu-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 36rpx 40rpx;
  border-bottom: 1px solid #f3f4f6;
  font-size: 28rpx;
  color: #1f2937;
}
.menu-item:last-child {
  border-bottom: none;
}
.contact-btn {
  background: transparent;
  text-align: left;
  line-height: normal;
  border: none;
  border-radius: 0;
  margin: 0;
}
.contact-btn::after {
  display: none;
}
.arrow {
  color: #9ca3af;
}
</style>
