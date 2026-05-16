<template>
  <view class="container">
    <!-- Top Banner -->
    <view class="banner" :class="{ 'has-bg': bannerUrl }">
      <image v-if="bannerUrl" class="banner-bg" :src="bannerUrl" mode="aspectFill" />
      <view class="banner-gradient">
        <text class="banner-title">舞榭歌台，一图尽收</text>
        <view class="banner-sub-row">
          <text class="banner-subtitle">腰未动，心先摇；足方举，意已飘。</text>
          <text class="banner-dot" v-if="currentCity">·</text>
          <view class="location-badge" v-if="currentCity">
            <text>{{ currentCity }}</text>
            <text class="location-icon">📍</text>
          </view>
        </view>
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

    <!-- Real-time Marquee -->
    <view class="marquee-container">
      <view class="marquee-label">
        <text class="dot"></text>
        <text>最新动态</text>
      </view>
      <view class="marquee-box">
        <view class="marquee-track" :style="{animationDuration: marqueeDuration}">
          <text class="marquee-item" v-for="(item, idx) in marqueeList" :key="idx">
            【{{ item.date }}】{{ item.text }}
          </text>
        </view>
      </view>
    </view>

    <!-- Filter -->
    <view class="filter-section scroll-x">
      <view :class="['filter-btn', !statusFilter ? 'active' : '']" @click="setStatusFilter(null)">全部</view>
      <view :class="['filter-btn', statusFilter === 'open' ? 'active' : '']" @click="setStatusFilter('open')">今日营业</view>
      <view :class="['filter-btn', statusFilter === 'closed' ? 'active' : '']" @click="setStatusFilter('closed')">今日停业</view>
      <view :class="['filter-btn', hotFilter ? 'active' : '']" @click="toggleHotFilter">🔥 热门</view>
    </view>

    <!-- Venue List -->
    <view class="venue-list">
      <view class="venue-card" v-for="(venue, index) in filteredVenues" :key="index" @click="goToDetail(venue.id)">
        <view class="card-header">
          <text class="venue-name">{{ venue.name }}</text>
          <view :class="['status-tag', getStatusClass(venue)]">
            {{ getStatusText(venue) }}
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
import { request } from '@/request.js'

const venues = ref([]);
const bannerUrl = ref('');
const statusFilter = ref(null); // 'open' | 'closed' | null
const hotFilter = ref(false);
const currentPage = ref(1);
const hasMore = ref(true);
const currentCity = ref('');
const userCoords = ref(null);

const marqueeList = ref([]);
const marqueeDuration = computed(() => {
  if (marqueeList.value.length === 0) return '20s';
  // 按每条 ~8 秒计算总时长，保证固定速度
  const total = marqueeList.value.reduce((sum, item) => {
    const len = (item.text || '').length + (item.date || '').length + 5;
    return sum + len;
  }, 0);
  // 每个字符约 0.3 秒，最少 15 秒
  return Math.max(15, total * 0.3) + 's';
});

const fetchVenues = (page = 1) => {
  if (!userCoords.value) return;
  const params = {
    page: page,
    page_size: 10,
    latitude: userCoords.value.latitude,
    longitude: userCoords.value.longitude
  };
  if (statusFilter.value === 'open') {
    params.open_status = 1;
  } else if (statusFilter.value === 'closed') {
    params.open_status = 0;
  }
  if (hotFilter.value) {
    params.hot = 1;
  }

  request({
    url: '/api/dance-halls',
    data: params,
    success: (res) => {
      if (res.data && res.data.code === 200) {
        const newData = res.data.data || [];
        if (res.data.current_city) {
          currentCity.value = res.data.current_city;
        }
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

const fetchReports = () => {
  if (!userCoords.value) return;
  request({
    url: '/api/reports',
    data: {
      latitude: userCoords.value.latitude,
      longitude: userCoords.value.longitude
    },
    success: (res) => {
      if (res.data && res.data.code === 200 && res.data.data) {
        marqueeList.value = res.data.data;
      }
    }
  });
};

const fetchBanner = () => {
  request({
    url: '/api/config',
    success: (res) => {
      if (res.data && res.data.code === 200 && res.data.data) {
        bannerUrl.value = res.data.data.banner_url || '';
      }
    }
  });
};

const showLocationFail = () => {
  uni.showModal({
    title: '定位失败',
    content: '无法获取您的位置，无法根据位置查看相关信息。请检查是否开启了定位权限。',
    showCancel: false,
    confirmText: '知道了'
  });
};

const getLocation = () => {
  return new Promise((resolve) => {
    // #ifdef MP-WEIXIN || APP-PLUS
    uni.getSetting({
      success: (settingRes) => {
        if (settingRes.authSetting['scope.userLocation'] === false) {
          // 用户之前拒绝过，引导去设置页开启
          uni.showModal({
            title: '定位权限',
            content: '需要获取您的位置才能推荐附近舞厅，请在设置中开启定位权限。',
            confirmText: '去设置',
            success: (modalRes) => {
              if (modalRes.confirm) {
                uni.openSetting({
                  success: (openRes) => {
                    if (openRes.authSetting['scope.userLocation']) {
                      doGetLocation(resolve);
                    } else {
                      showLocationFail();
                      resolve();
                    }
                  }
                });
              } else {
                showLocationFail();
                resolve();
              }
            }
          });
        } else {
          // 未授权过或已授权，直接请求定位
          doGetLocation(resolve);
        }
      }
    });
    // #endif
    // #ifndef MP-WEIXIN || APP-PLUS
    resolve();
    // #endif
  });
};

const doGetLocation = (resolve) => {
  uni.getLocation({
    type: 'gcj02',
    success: (res) => {
      userCoords.value = {
        latitude: res.latitude,
        longitude: res.longitude
      };
      resolve();
    },
    fail: () => {
      showLocationFail();
      resolve();
    }
  });
};

const parseTimeRange = (str) => {
  if (!str) return null;
  const m = str.match(/(\d{1,2}):(\d{2})\s*[-~—]\s*(\d{1,2}):(\d{2})/);
  if (!m) return null;
  return { start: parseInt(m[1]) * 60 + parseInt(m[2]), end: parseInt(m[3]) * 60 + parseInt(m[4]) };
};

const isInBusinessHours = (venue) => {
  const now = new Date();
  const nowMin = now.getHours() * 60 + now.getMinutes();
  const ranges = [venue.morning_hours, venue.afternoon_hours, venue.evening_hours]
    .map(parseTimeRange)
    .filter(Boolean);
  if (ranges.length === 0) return true; // 没有时间数据默认算营业中
  return ranges.some(r => nowMin >= r.start && nowMin <= r.end);
};

const getStatusText = (venue) => {
  if (!venue.open_status) return '暂停营业';
  if (!isInBusinessHours(venue)) return '未到营业时间';
  return '营业中';
};

const getStatusClass = (venue) => {
  if (!venue.open_status) return 'status-closed';
  if (!isInBusinessHours(venue)) return 'status-waiting';
  return 'status-open';
};

onMounted(() => {
  fetchBanner();
  getLocation().then(() => {
    fetchReports();
    fetchVenues(1);
  });
});

onReachBottom(() => {
  if (hasMore.value) {
    currentPage.value += 1;
    fetchVenues(currentPage.value);
  }
});

const setStatusFilter = (status) => {
  statusFilter.value = status;
  currentPage.value = 1;
  hasMore.value = true;
  venues.value = [];
  fetchVenues(1);
};

const toggleHotFilter = () => {
  hotFilter.value = !hotFilter.value;
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
  height: 300rpx;
  background: linear-gradient(135deg, #1e3a5f 0%, #0f172a 100%);
  position: relative;
  overflow: hidden;
}
.banner.has-bg {
  background: none;
}
.banner-bg {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
}
.banner-gradient {
  position: relative;
  z-index: 1;
  width: 100%;
  height: 100%;
  padding: 50rpx 40rpx;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  justify-content: center;
}
.has-bg .banner-gradient {
  background: linear-gradient(180deg, rgba(0,0,0,0.1) 0%, rgba(0,0,0,0.4) 100%);
}
.banner-title {
  font-size: 40rpx;
  font-weight: bold;
  color: #ffffff;
  letter-spacing: 2rpx;
  margin-bottom: 12rpx;
  text-shadow: 0 2rpx 8rpx rgba(0,0,0,0.3);
}
.banner-subtitle {
  font-size: 24rpx;
  color: rgba(255,255,255,0.8);
}
.banner-sub-row {
  display: flex;
  align-items: center;
  margin-top: 12rpx;
  flex-wrap: wrap;
}
.banner-dot {
  font-size: 24rpx;
  color: rgba(255,255,255,0.5);
  margin: 0 12rpx;
}
.location-badge {
  display: inline-flex;
  align-items: center;
  background: rgba(255, 255, 255, 0.2);
  padding: 6rpx 18rpx;
  border-radius: 30rpx;
}
.location-icon {
  font-size: 22rpx;
  margin-left: 6rpx;
}
.location-badge text {
  font-size: 24rpx;
  color: #ffffff;
  font-weight: 500;
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
.marquee-container {
  display: flex;
  align-items: center;
  background: #f9fafb;
  border: 1px solid #e5e7eb;
  margin: 0 24rpx 30rpx;
  padding: 16rpx 24rpx;
  border-radius: 16rpx;
  overflow: hidden;
}
.marquee-label {
  display: flex;
  align-items: center;
  font-size: 26rpx;
  font-weight: bold;
  color: #111827;
  margin-right: 20rpx;
  white-space: nowrap;
}
.dot {
  width: 12rpx;
  height: 12rpx;
  background: #10b981;
  border-radius: 50%;
  margin-right: 12rpx;
}
.marquee-box {
  flex: 1;
  overflow: hidden;
  position: relative;
  height: 40rpx;
  display: flex;
  align-items: center;
}
.marquee-track {
  display: flex;
  white-space: nowrap;
  animation: scroll-text linear infinite;
}
.marquee-item {
  font-size: 26rpx;
  color: #374151;
  margin-right: 80rpx;
}
@keyframes scroll-text {
  0% {
    transform: translateX(100%);
  }
  100% {
    transform: translateX(-100%);
  }
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
.status-waiting {
  background: rgba(245, 158, 11, 0.1);
  color: #f59e0b;
  border: 1px solid rgba(245, 158, 11, 0.2);
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
