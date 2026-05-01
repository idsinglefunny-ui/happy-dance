<template>
  <view class="container">
    <view class="user-info">
      <view class="avatar"></view>
      <text class="nickname">微信用户</text>
    </view>
    
    <view class="menu-list">
      <view class="menu-item" @click="goToClaim">
        <text>认领舞厅 / 商家入口</text>
        <text class="arrow">></text>
      </view>
      <button class="menu-item contact-btn" open-type="contact">
        <text>联系平台客服</text>
        <text class="arrow">></text>
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
  background-color: #0b0b0e;
  color: #ffffff;
}
.container {
  padding: 24rpx;
}
.user-info {
  display: flex;
  align-items: center;
  margin-bottom: 40rpx;
  padding: 40rpx 20rpx;
  background: #15151e;
  border-radius: 16rpx;
}
.avatar {
  width: 120rpx;
  height: 120rpx;
  background: #2a2a36;
  border-radius: 60rpx;
  margin-right: 30rpx;
}
.nickname {
  font-size: 36rpx;
  font-weight: bold;
}
.menu-list {
  background: #15151e;
  border-radius: 16rpx;
  overflow: hidden;
}
.menu-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 30rpx 40rpx;
  border-bottom: 1px solid #2a2a36;
  font-size: 28rpx;
  color: #dddddd;
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
  color: #555555;
}
</style>
