<template>
  <view class="container">
    <view class="header-notice">
      <text class="title">认领须知</text>
      <text class="desc">认领成功后，您可免费管理舞厅信息，及时发布营业及活动信息。平台将在1-3个工作日内审核您的申请。</text>
    </view>

    <form @submit="submitForm">
      <view class="form-group">
        <text class="group-title">舞厅基本信息</text>
        <view class="input-item">
          <text class="label"><text class="required">*</text> 舞厅名称</text>
          <input class="input" name="venue_name" placeholder="请输入舞厅名称" placeholder-class="ph" />
        </view>
        <view class="input-item">
          <text class="label"><text class="required">*</text> 所在城市</text>
          <input class="input" name="city" placeholder="请输入所在城市，如：成都" placeholder-class="ph" />
        </view>
        <view class="input-item">
          <text class="label"><text class="required">*</text> 舞厅地址</text>
          <view class="address-box">
            <input class="input addr-input" name="address" placeholder="请输入或点击右侧图标选择" placeholder-class="ph" />
            <view class="location-icon" @click="chooseLocation">📍</view>
          </view>
        </view>
      </view>

      <view class="form-group">
        <text class="group-title">申请人信息</text>
        <view class="input-item">
          <text class="label"><text class="required">*</text> 真实姓名</text>
          <input class="input" name="applicant_name" placeholder="请输入真实姓名" placeholder-class="ph" />
        </view>
        <view class="input-item">
          <text class="label"><text class="required">*</text> 手机号</text>
          <input class="input" name="contact_phone" type="number" placeholder="请输入手机号" placeholder-class="ph" />
        </view>
        <view class="input-item">
          <text class="label"><text class="required">*</text> 微信号</text>
          <input class="input" name="contact_wechat" placeholder="请输入微信号" placeholder-class="ph" />
        </view>
        <view class="input-item">
          <text class="label"><text class="required">*</text> 与舞厅的关系</text>
          <radio-group name="relationship" class="radio-group">
            <label class="radio-label"><radio value="老板" color="#111827" /> 老板</label>
            <label class="radio-label"><radio value="经理" color="#111827" /> 经理</label>
            <label class="radio-label"><radio value="工作人员" color="#111827" /> 员工</label>
          </radio-group>
        </view>
      </view>

      <view class="form-group">
        <text class="group-title">资质证明 (营业执照等)</text>
        <view class="upload-box" @click="chooseImage">
          <text class="upload-icon">+</text>
          <text class="upload-text">添加图片</text>
        </view>
      </view>

      <view class="submit-section">
        <label class="agreement">
          <checkbox color="#111827" style="transform:scale(0.8)" /> 同意《商家签署协议》
        </label>
        <button class="submit-btn" form-type="submit">提交认领申请</button>
      </view>
    </form>
  </view>
</template>

<script setup>
const chooseLocation = () => {
  uni.chooseLocation({
    success: (res) => {
      uni.showToast({ title: '已获取位置', icon: 'none' })
    }
  })
};

const chooseImage = () => {
  uni.chooseImage({
    count: 3,
    success: (res) => {
      uni.showToast({ title: '已选择图片', icon: 'none' })
    }
  })
};

const submitForm = (e) => {
  const data = e.detail.value;
  uni.request({
    url: 'http://localhost:12800/api/claims',
    method: 'POST',
    data: data,
    success: (res) => {
      if(res.data && res.data.code === 200) {
        uni.showToast({ title: '提交成功，请等待审核', icon: 'none' });
        setTimeout(() => uni.navigateBack(), 1500);
      } else {
        uni.showToast({ title: '提交失败', icon: 'none' });
      }
    },
    fail: () => {
      uni.showToast({ title: '网络请求失败', icon: 'none' });
    }
  });
};
</script>

<style>
page {
  background-color: #ffffff;
  color: #1f2937;
}
.container {
  padding: 24rpx;
  padding-bottom: 100rpx;
}
.header-notice {
  background: #f3f4f6;
  border: 1px solid #e5e7eb;
  padding: 24rpx;
  border-radius: 16rpx;
  margin-bottom: 32rpx;
}
.title {
  color: #1f2937;
  font-weight: bold;
  font-size: 28rpx;
  display: block;
  margin-bottom: 10rpx;
}
.desc {
  color: #4b5563;
  font-size: 24rpx;
  line-height: 1.6;
}
.form-group {
  background: #ffffff;
  border-radius: 20rpx;
  padding: 32rpx;
  margin-bottom: 32rpx;
  border: 1px solid #e5e7eb;
}
.group-title {
  font-size: 30rpx;
  font-weight: bold;
  margin-bottom: 32rpx;
  display: block;
  color: #111827;
}
.input-item {
  margin-bottom: 32rpx;
}
.input-item:last-child {
  margin-bottom: 0;
}
.label {
  font-size: 26rpx;
  color: #374151;
  margin-bottom: 16rpx;
  display: block;
}
.required {
  color: #ef4444;
  margin-right: 4rpx;
}
.input {
  background: #ffffff;
  height: 88rpx;
  border-radius: 12rpx;
  padding: 0 24rpx;
  color: #111827;
  font-size: 28rpx;
  border: 1px solid #d1d5db;
  box-sizing: border-box;
}
.ph {
  color: #9ca3af;
}
.address-box {
  display: flex;
  align-items: center;
}
.addr-input {
  flex: 1;
}
.location-icon {
  width: 88rpx;
  height: 88rpx;
  background: #f3f4f6;
  margin-left: 16rpx;
  border-radius: 12rpx;
  border: 1px solid #d1d5db;
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 32rpx;
  box-sizing: border-box;
}
.radio-group {
  display: flex;
  justify-content: space-between;
}
.radio-label {
  font-size: 28rpx;
  display: flex;
  align-items: center;
  color: #4b5563;
}
.upload-box {
  width: 170rpx;
  height: 170rpx;
  border: 1px dashed #d1d5db;
  border-radius: 12rpx;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  background: #f9fafb;
}
.upload-icon {
  font-size: 64rpx;
  color: #9ca3af;
  margin-bottom: 8rpx;
  line-height: 1;
}
.upload-text {
  font-size: 22rpx;
  color: #6b7280;
}
.submit-section {
  margin-top: 48rpx;
}
.agreement {
  font-size: 24rpx;
  color: #4b5563;
  display: flex;
  align-items: center;
  margin-bottom: 24rpx;
}
.submit-btn {
  background: #111827;
  color: #ffffff;
  border-radius: 44rpx;
  font-size: 32rpx;
  font-weight: bold;
  border: none;
  height: 88rpx;
  display: flex;
  justify-content: center;
  align-items: center;
}
.submit-btn::after {
  display: none;
}
</style>
