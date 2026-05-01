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
            <label class="radio-label"><radio value="老板" color="#e5007f" /> 老板</label>
            <label class="radio-label"><radio value="经理" color="#e5007f" /> 经理</label>
            <label class="radio-label"><radio value="工作人员" color="#e5007f" /> 员工</label>
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
          <checkbox color="#e5007f" style="transform:scale(0.8)" /> 同意《商家签署协议》
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
      // 可以在这里回填地址
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
    url: 'http://localhost:8080/api/claims',
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
  background-color: #0b0b0e;
  color: #ffffff;
}
.container {
  padding: 24rpx;
  padding-bottom: 100rpx;
}
.header-notice {
  background: rgba(229, 0, 127, 0.1);
  border: 1px solid rgba(229, 0, 127, 0.3);
  padding: 20rpx;
  border-radius: 12rpx;
  margin-bottom: 30rpx;
}
.title {
  color: #e5007f;
  font-weight: bold;
  font-size: 28rpx;
  display: block;
  margin-bottom: 10rpx;
}
.desc {
  color: #bbbbbb;
  font-size: 24rpx;
  line-height: 1.5;
}
.form-group {
  background: #15151e;
  border-radius: 16rpx;
  padding: 30rpx;
  margin-bottom: 30rpx;
}
.group-title {
  font-size: 32rpx;
  font-weight: bold;
  margin-bottom: 30rpx;
  display: block;
  color: #fff;
}
.input-item {
  margin-bottom: 30rpx;
}
.label {
  font-size: 28rpx;
  color: #dddddd;
  margin-bottom: 16rpx;
  display: block;
}
.required {
  color: #ff4040;
}
.input {
  background: #1e1e28;
  height: 80rpx;
  border-radius: 8rpx;
  padding: 0 20rpx;
  color: #ffffff;
  font-size: 28rpx;
}
.ph {
  color: #555555;
}
.address-box {
  display: flex;
  align-items: center;
}
.addr-input {
  flex: 1;
}
.location-icon {
  width: 80rpx;
  height: 80rpx;
  background: #2a2a36;
  margin-left: 10rpx;
  border-radius: 8rpx;
  display: flex;
  justify-content: center;
  align-items: center;
}
.radio-group {
  display: flex;
  justify-content: space-between;
}
.radio-label {
  font-size: 28rpx;
  display: flex;
  align-items: center;
  color: #ccc;
}
.upload-box {
  width: 160rpx;
  height: 160rpx;
  border: 1px dashed #e5007f;
  border-radius: 8rpx;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  background: rgba(229, 0, 127, 0.05);
}
.upload-icon {
  font-size: 60rpx;
  color: #e5007f;
  margin-bottom: 10rpx;
  line-height: 1;
}
.upload-text {
  font-size: 22rpx;
  color: #e5007f;
}
.submit-section {
  margin-top: 40rpx;
}
.agreement {
  font-size: 24rpx;
  color: #888888;
  display: flex;
  align-items: center;
  margin-bottom: 20rpx;
}
.submit-btn {
  background: linear-gradient(90deg, #e5007f, #9900ff);
  color: #ffffff;
  border-radius: 40rpx;
  font-size: 32rpx;
  font-weight: bold;
  border: none;
}
</style>
