<template>
  <view class="container">
    <!-- Top Banner -->
    <view class="banner">
      <view class="banner-gradient">
        <text class="banner-title">全国最火爆的莎莎舞厅</text>
        <text class="banner-subtitle">探索全国舞讯 · 计时体验升级</text>
      </view>
    </view>

    <!-- Quick Navigation -->
    <view class="nav-grid">
      <view class="nav-item" @click="goToClaim">
        <text class="nav-icon">✨</text>
        <text class="nav-text">认领舞厅</text>
      </view>
      <view class="nav-item" @click="goToTimer">
        <text class="nav-icon">⏱️</text>
        <text class="nav-text">专属计时</text>
      </view>
    </view>

    <!-- Real-time Marquee / Bullet Screen -->
    <view class="marquee-section">
      <view class="marquee-header">
        <view class="marquee-title">
          <text class="dot"></text>
          <text>实时弹幕区</text>
        </view>
        <view class="marquee-actions">
          <text class="action-btn">查看全部 →</text>
        </view>
      </view>
      <swiper class="marquee-swiper" vertical autoplay circular interval="3000" :show-indicators="false">
        <swiper-item v-for="(item, idx) in marqueeList" :key="idx">
          <view class="marquee-content">
            <view class="marquee-main">
              <text class="marquee-date">{{ item.date }}</text>
              <text class="marquee-text">{{ item.text }}</text>
            </view>
          </view>
        </swiper-item>
      </swiper>
    </view>

    <!-- Filter -->
    <view class="filter-section scroll-x">
      <view :class="['filter-btn', currentFilter === 'all' ? 'active' : '']" @click="setFilter('all')">全部</view>
      <view :class="['filter-btn', currentFilter === 'open' ? 'active' : '']" @click="setFilter('open')">今日营业</view>
      <view :class="['filter-btn', currentFilter === 'closed' ? 'active' : '']" @click="setFilter('closed')">今日停业</view>
      <view :class="['filter-btn', currentFilter === 'hot' ? 'active' : '']" @click="setFilter('hot')">🔥 热门</view>
    </view>

    <!-- Venue List -->
    <view class="venue-list">
      <view class="venue-card" v-for="(venue, index) in filteredVenues" :key="index" @click="goToDetail(venue.id)">
        <view class="card-header">
          <text class="venue-name">{{ venue.name }}</text>
          <view :class="['status-tag', venue.open_status ? 'status-open' : 'status-closed']">
            {{ venue.open_status ? '营业中' : '休息中' }}
          </view>
        </view>
        
        <view class="card-body">
          <text class="venue-hours">营业时间: {{ venue.afternoon_hours || '下午场' }} / {{ venue.evening_hours || '晚场' }}</text>
        </view>
        
        <view class="card-footer">
          <text class="venue-address">{{ venue.city }} · {{ venue.address }}</text>
          <view class="distance-box">
            <text class="distance-text">{{ venue.distance_display || '计算中' }}</text>
            <text class="nav-arrow">➔</text>
          </view>
        </view>
      </view>

      <!-- Pagination / Loading States -->
      <view class="loading-state" v-if="venues.length > 0">
        <text v-if="hasMore">正在加载更多...</text>
        <text v-else>已加载全部数据</text>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { onReachBottom } from '@dcloudio/uni-app';

const venues = ref([]);
const currentFilter = ref('all');
const currentPage = ref(1);
const hasMore = ref(true);

const marqueeList = ref([
  { date: '05-01', text: '金卡罗 临时停业，大家别跑空了', user: '悉达多', time: '1分钟前' },
  { date: '05-01', text: '迪乐汇歌舞厅 晚场满场，气氛极佳！', user: '舞王', time: '5分钟前' },
  { date: '05-01', text: '星海壹号 下午 暂停营业', user: '匿名用户', time: '10分钟前' }
]);

const fetchVenues = (page = 1) => {
  const params = {
    page: page,
    page_size: 10,
    latitude: 30.6586,
    longitude: 104.0648
  };
  if (currentFilter.value === 'open') {
    params.open_status = 1;
  } else if (currentFilter.value === 'closed') {
    params.open_status = 0;
  } else if (currentFilter.value === 'hot') {
    params.hot = 1;
  }

  uni.request({
    url: 'http://localhost:12800/api/dance-halls',
    data: params,
    success: (res) => {
      if (res.data && res.data.code === 200) {
        const newData = res.data.data || [];
        if (page === 1) {
          venues.value = newData;
        } else {
          venues.value = [...venues.value, ...newData];
        }
        if (newData.length < 10) {
          hasMore.value = false;
        } else {
          hasMore.value = true;
        }
      }
    }
  });
};

onMounted(() => {
  fetchVenues(1);
});

onReachBottom(() => {
  if (hasMore.value) {
    currentPage.value += 1;
    fetchVenues(currentPage.value);
  }
});

const setFilter = (type) => {
  currentFilter.value = type;
  currentPage.value = 1;
  hasMore.value = true;
  venues.value = [];
  fetchVenues(1);
};

const goToDetail = (id) => {
  if(id) {
    uni.navigateTo({
      url: `/pages/detail/detail?id=${id}`
    });
  }
};

const goToTimer = () => {
  uni.navigateTo({
    url: '/pages/timer/timer'
  });
};

const goToClaim = () => {
  uni.navigateTo({
    url: '/pages/claim/claim'
  });
};

const filteredVenues = computed(() => {
  return venues.value;
});
</script>

<style>
page {
  background-color: #ffffff;
  color: #1f2937;
}
.container {
  padding-bottom: 40rpx;
  background-color: #ffffff;
}
.banner {
  width: 100%;
  height: 240rpx;
  background: #f3f4f6;
  position: relative;
  overflow: hidden;
}
.banner-gradient {
  width: 100%;
  height: 100%;
  padding: 40rpx;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  justify-content: center;
}
.banner-title {
  font-size: 38rpx;
  font-weight: bold;
  color: #111827;
  letter-spacing: 2rpx;
  margin-bottom: 12rpx;
}
.banner-subtitle {
  font-size: 24rpx;
  color: #6b7280;
}
.nav-grid {
  display: flex;
  justify-content: space-around;
  padding: 36rpx 20rpx;
  background-color: #ffffff;
  border-bottom: 1px solid #e5e7eb;
  margin-bottom: 24rpx;
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
  font-size: 52rpx;
  margin-bottom: 12rpx;
}
.nav-text {
  font-size: 26rpx;
  color: #374151;
}

/* Marquee / Bullet Screen Styles */
.marquee-section {
  background: #ffffff;
  margin: 0 24rpx 30rpx;
  border-radius: 20rpx;
  padding: 24rpx;
  border: 1px solid #e5e7eb;
}
.marquee-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20rpx;
}
.marquee-title {
  display: flex;
  align-items: center;
  font-size: 28rpx;
  font-weight: bold;
  color: #111827;
}
.dot {
  width: 14rpx;
  height: 14rpx;
  background: #10b981;
  border-radius: 50%;
  margin-right: 14rpx;
}
.marquee-actions {
  display: flex;
  align-items: center;
}
.action-btn {
  font-size: 24rpx;
  color: #6b7280;
  margin-left: 20rpx;
}
.report-btn {
  background: #f3f4f6;
  color: #374151;
  padding: 6rpx 20rpx;
  border-radius: 30rpx;
  border: 1px solid #d1d5db;
}
.marquee-swiper {
  height: 130rpx;
  background: #f9fafb;
  border-radius: 16rpx;
  border: 1px solid #e5e7eb;
}
.marquee-content {
  padding: 24rpx;
  height: 100%;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}
.marquee-main {
  font-size: 28rpx;
  color: #374151;
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.marquee-date {
  color: #2563eb;
  margin-right: 14rpx;
  font-weight: bold;
}
.marquee-user {
  display: flex;
  align-items: center;
  font-size: 24rpx;
  color: #6b7280;
}
.user-avatar {
  width: 32rpx;
  height: 32rpx;
  border-radius: 50%;
  background: #e5e7eb;
  margin-right: 12rpx;
}
.marquee-time {
  margin-left: auto;
}

.filter-section {
  display: flex;
  padding: 0 24rpx;
  margin-bottom: 24rpx;
  overflow-x: auto;
  white-space: nowrap;
}
.filter-btn {
  padding: 12rpx 32rpx;
  border-radius: 32rpx;
  background: #f3f4f6;
  color: #4b5563;
  font-size: 26rpx;
  margin-right: 20rpx;
  flex-shrink: 0;
  border: 1px solid #e5e7eb;
}
.filter-btn.active {
  background: #111827;
  color: #ffffff;
  border: 1px solid #111827;
}
.venue-list {
  padding: 0 24rpx;
}
.venue-card {
  background: #ffffff;
  border-radius: 20rpx;
  padding: 32rpx;
  margin-bottom: 24rpx;
  border: 1px solid #e5e7eb;
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
  color: #111827;
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
.card-body {
  margin-bottom: 24rpx;
}
.venue-hours {
  font-size: 26rpx;
  color: #4b5563;
  display: block;
}
.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
}
.venue-address {
  font-size: 24rpx;
  color: #6b7280;
  max-width: 70%;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.distance-box {
  display: flex;
  align-items: center;
  background: #f3f4f6;
  padding: 10rpx 24rpx;
  border-radius: 30rpx;
  border: 1px solid #d1d5db;
}
.distance-text {
  font-size: 24rpx;
  font-weight: bold;
  color: #1f2937;
  margin-right: 8rpx;
}
.nav-arrow {
  font-size: 22rpx;
  color: #4b5563;
}
.loading-state {
  text-align: center;
  padding: 30rpx 0;
  color: #6b7280;
  font-size: 24rpx;
}
</style>
