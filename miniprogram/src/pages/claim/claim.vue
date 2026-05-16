<template>
  <view class="container">
    <!-- 认领须知 -->
    <view class="header-notice">
      <text class="notice-title">ⓘ 认领须知</text>
      <text class="notice-desc">认领成功后，您可免费管理舞厅信息，及时发布营业及活动信息。平台将在 1-3 个工作日内审核您的申请。</text>
    </view>

    <!-- 商家操作手册 -->
    <view class="manual-section">
      <text class="manual-title">商家操作手册</text>
      <view class="manual-item">
        <text class="manual-num">①</text>
        <view class="manual-content">
          <text class="manual-subtitle">认领审核</text>
          <text class="manual-text">提交申请后，平台将在 1-3 个工作日内完成审核，审核结果将通过小程序消息通知您。</text>
        </view>
      </view>
      <view class="manual-item">
        <text class="manual-num">②</text>
        <view class="manual-content">
          <text class="manual-subtitle">信息维护</text>
          <text class="manual-text">认领成功后，您可编辑基础信息、营业时间、门票价格等，请保持信息及时准确。</text>
        </view>
      </view>
      <view class="manual-item">
        <text class="manual-num">③</text>
        <view class="manual-content">
          <text class="manual-subtitle">经营状态维护（重要）</text>
          <text class="manual-text">请务必及时维护舞厅的经营状态，确保用户看到的状态与实际情况一致：</text>
          <view class="status-examples">
            <view class="status-row">
              <text class="status-badge status-open-badge">营业中</text>
              <text class="status-arrow">→</text>
              <text class="status-desc">恢复营业时，请将经营状态由「停业」改为「营业」</text>
            </view>
            <view class="status-row">
              <text class="status-badge status-closed-badge">已停业</text>
              <text class="status-arrow">→</text>
              <text class="status-desc">停业时，请将经营状态由「营业」改为「停业」</text>
            </view>
          </view>
        </view>
      </view>
      <view class="manual-item">
        <text class="manual-num">④</text>
        <view class="manual-content">
          <text class="manual-subtitle">数据更新提醒</text>
          <text class="manual-text">请在信息发生变更后第一时间进行更新。有过不及时更新数据记录的商家将被平台标注，影响展示效果。</text>
        </view>
      </view>
    </view>

    <!-- 舞厅基本信息 -->
    <form @submit="submitForm">
      <view class="form-group">
        <text class="group-title">舞厅基本信息</text>
        <view class="input-item">
          <text class="label"><text class="required">*</text> 舞厅名称</text>
          <input class="input" name="venue_name" placeholder="请输入舞厅名称" placeholder-class="ph" />
        </view>
        <view class="input-item">
          <text class="label"><text class="required">*</text> 所在城市</text>
          <input class="input" name="city" :value="formCity" @input="formCity = $event.detail.value" placeholder="请输入所在城市，如：成都" placeholder-class="ph" />
        </view>
        <view class="input-item">
          <text class="label"><text class="required">*</text> 舞厅地址</text>
          <view class="address-box">
            <input class="input addr-input" name="address" :value="formAddress" @input="formAddress = $event.detail.value" placeholder="请输入或点击右侧图标选择" placeholder-class="ph" />
            <view class="location-btn" @click="chooseLocation">📍</view>
          </view>
        </view>
      </view>

      <!-- 申请人信息 -->
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

      <!-- 资质证明 -->
      <view class="form-group">
        <text class="group-title">资质证明（营业执照等）</text>
        <view class="upload-box" @click="chooseImage">
          <text class="upload-icon">+</text>
          <text class="upload-text">添加图片</text>
        </view>
      </view>

      <!-- 提交 -->
      <view class="submit-section">
        <label class="agreement" @click="toggleAgreement">
          <view :class="['checkbox', agreed ? 'checked' : '']">
            <text v-if="agreed" class="check-mark">✓</text>
          </view>
          <text class="agreement-text">同意《<text class="agreement-link" @click.stop="showAgreement">商家签署协议</text>》</text>
        </label>
        <button class="submit-btn" :class="{ disabled: !agreed }" :disabled="!agreed" form-type="submit">提交认领申请</button>
      </view>
    </form>

    <!-- 协议弹窗 -->
    <view class="modal-mask" v-if="showAgreementModal" @click="showAgreementModal = false">
      <view class="modal-content" @click.stop>
        <view class="modal-scroll">
          <text class="modal-title">商家签署协议</text>

          <text class="article-title">第一条 服务内容</text>
          <text class="article-text">甲方（平台）为乙方（商家）提供舞厅信息展示、管理及运营状态发布等服务。乙方通过认领舞厅获得该舞厅的信息管理权限。</text>

          <text class="article-title">第二条 资质与合规</text>
          <text class="article-text">1. 乙方应确保其经营的舞厅已依法取得相关营业资质，符合"娱乐场所服务"类目要求。</text>
          <text class="article-text">2. 乙方应对其上传资料的真实性、合法性和有效性承担全部责任，确保经营行为符合国家及地方相关法律法规。</text>

          <text class="article-title">第三条 数据维护义务</text>
          <text class="article-text">1. 乙方有义务在信息发生变更后第一时间进行更新，包括但不限于营业时间、门票价格、活动信息、联系方式等，确保展示内容与实际经营情况一致。</text>
          <text class="article-text">2. 因信息滞后或错误导致用户产生纠纷的，责任由乙方自行承担。</text>
          <text class="article-text">3. 有过不及时更新数据记录的商家，平台有权对其进行标注提示，情节严重者可暂停其展示资格。</text>

          <text class="article-title">第四条 平台免责与权利</text>
          <text class="article-text">1. 如乙方存在违法经营、虚假宣传、未依法取得许可等行为，平台有权立即下架其展示信息，并向相关主管部门报告。</text>
          <text class="article-text">2. 因乙方经营行为引发的所有纠纷和法律责任，由乙方自行承担，平台不承担任何连带责任。</text>

          <text class="article-title">第五条 协议的签署与生效</text>
          <text class="article-text">1. 本协议采用电子签署方式，一经乙方在小程序上点击"我已知晓并同意协议"即视为签署并同意本协议，本协议即刻生效。</text>
          <text class="article-text">2. 平台有权随时更新本协议条款，更新后在小程序公告生效。如乙方不同意更新，应停止使用平台服务；继续使用视为接受更新。</text>
        </view>
        <view class="modal-footer">
          <view class="modal-btn" @click="acceptAgreement">我已知晓并同意协议</view>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref } from 'vue';
import { request } from '@/request.js'

const formCity = ref('');
const formAddress = ref('');
const agreed = ref(false);
const showAgreementModal = ref(false);

const chooseLocation = () => {
  uni.chooseLocation({
    success: (res) => {
      formAddress.value = res.address || '';
      // 从地址中提取城市
      if (res.address) {
        const match = res.address.match(/(.*?省)?(.*?市)/);
        if (match && match[2]) {
          formCity.value = match[2].replace('市', '');
        }
      }
    },
    fail: (err) => {
      console.warn('选择位置失败:', err);
      uni.showToast({ title: '选择位置失败', icon: 'none' });
    }
  });
};

const chooseImage = () => {
  uni.chooseImage({
    count: 3,
    success: (res) => {
      uni.showToast({ title: '已选择图片', icon: 'none' });
    }
  });
};

const toggleAgreement = () => {
  agreed.value = !agreed.value;
};

const showAgreement = () => {
  showAgreementModal.value = true;
};

const acceptAgreement = () => {
  agreed.value = true;
  showAgreementModal.value = false;
};

const submitForm = (e) => {
  const data = e.detail.value;
  if (!data.venue_name || !data.city || !data.address || !data.applicant_name || !data.contact_phone || !data.contact_wechat || !data.relationship) {
    uni.showToast({ title: '请填写完整信息', icon: 'none' });
    return;
  }
  if (!agreed.value) {
    uni.showToast({ title: '请先同意商家签署协议', icon: 'none' });
    return;
  }
  request({
    url: '/api/claims',
    method: 'POST',
    data: data,
    success: (res) => {
      if (res.data && res.data.code === 200) {
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
  background-color: #f5f5f5;
  color: #1f2937;
}
.container {
  padding: 24rpx;
  padding-bottom: 100rpx;
}

/* 认领须知 */
.header-notice {
  background: linear-gradient(135deg, rgba(17,24,39,0.04) 0%, rgba(17,24,39,0.08) 100%);
  padding: 28rpx;
  border-radius: 16rpx;
  margin-bottom: 24rpx;
  border-left: 6rpx solid #111827;
}
.notice-title {
  color: #111827;
  font-weight: bold;
  font-size: 28rpx;
  display: block;
  margin-bottom: 12rpx;
}
.notice-desc {
  color: #4b5563;
  font-size: 24rpx;
  line-height: 1.8;
}

/* 商家操作手册 */
.manual-section {
  background: #ffffff;
  border-radius: 16rpx;
  padding: 28rpx;
  margin-bottom: 24rpx;
  border: 1px solid #e5e7eb;
}
.manual-title {
  font-size: 30rpx;
  font-weight: bold;
  color: #111827;
  display: block;
  margin-bottom: 24rpx;
}
.manual-item {
  display: flex;
  margin-bottom: 24rpx;
}
.manual-item:last-child {
  margin-bottom: 0;
}
.manual-num {
  font-size: 28rpx;
  font-weight: bold;
  color: #111827;
  margin-right: 16rpx;
  flex-shrink: 0;
  margin-top: 2rpx;
}
.manual-content {
  flex: 1;
}
.manual-subtitle {
  font-size: 28rpx;
  font-weight: bold;
  color: #111827;
  display: block;
  margin-bottom: 8rpx;
}
.manual-text {
  font-size: 24rpx;
  color: #6b7280;
  line-height: 1.7;
}
.status-examples {
  margin-top: 16rpx;
}
.status-row {
  display: flex;
  align-items: center;
  margin-bottom: 12rpx;
}
.status-row:last-child {
  margin-bottom: 0;
}
.status-badge {
  font-size: 22rpx;
  font-weight: bold;
  padding: 4rpx 16rpx;
  border-radius: 6rpx;
  flex-shrink: 0;
}
.status-open-badge {
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
  border: 1px solid rgba(16, 185, 129, 0.3);
}
.status-closed-badge {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
  border: 1px solid rgba(239, 68, 68, 0.3);
}
.status-arrow {
  margin: 0 12rpx;
  color: #9ca3af;
  font-size: 22rpx;
}
.status-desc {
  font-size: 22rpx;
  color: #6b7280;
  flex: 1;
}

/* 表单 */
.form-group {
  background: #ffffff;
  border-radius: 16rpx;
  padding: 28rpx;
  margin-bottom: 24rpx;
  border: 1px solid #e5e7eb;
}
.group-title {
  font-size: 30rpx;
  font-weight: bold;
  margin-bottom: 28rpx;
  display: block;
  color: #111827;
}
.input-item {
  margin-bottom: 28rpx;
}
.input-item:last-child {
  margin-bottom: 0;
}
.label {
  font-size: 26rpx;
  color: #374151;
  margin-bottom: 14rpx;
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
  width: 100%;
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
.location-btn {
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

/* 提交区 */
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
.checkbox {
  width: 32rpx;
  height: 32rpx;
  border: 2rpx solid #d1d5db;
  border-radius: 6rpx;
  margin-right: 12rpx;
  display: flex;
  justify-content: center;
  align-items: center;
  flex-shrink: 0;
}
.checkbox.checked {
  background: #111827;
  border-color: #111827;
}
.check-mark {
  color: #ffffff;
  font-size: 22rpx;
  font-weight: bold;
}
.agreement-text {
  font-size: 24rpx;
  color: #4b5563;
}
.agreement-link {
  color: #111827;
  font-weight: bold;
  text-decoration: underline;
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
.submit-btn.disabled {
  background: #9ca3af;
  color: #d1d5db;
}
.submit-btn::after {
  display: none;
}

/* 协议弹窗 */
.modal-mask {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: 999;
  display: flex;
  justify-content: center;
  align-items: center;
}
.modal-content {
  width: 85%;
  max-width: 85%;
  max-height: 80vh;
  background: #ffffff;
  border-radius: 24rpx;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  box-sizing: border-box;
}
.modal-scroll {
  padding: 40rpx;
  max-height: 60vh;
  overflow-y: auto;
  -webkit-overflow-scrolling: touch;
}
.modal-title {
  font-size: 34rpx;
  font-weight: bold;
  color: #111827;
  display: block;
  text-align: center;
  margin-bottom: 32rpx;
}
.article-title {
  font-size: 28rpx;
  font-weight: bold;
  color: #111827;
  display: block;
  margin-top: 24rpx;
  margin-bottom: 12rpx;
}
.article-text {
  font-size: 24rpx;
  color: #4b5563;
  line-height: 1.8;
  display: block;
  margin-bottom: 8rpx;
  word-break: break-all;
  white-space: normal;
}
.modal-footer {
  padding: 24rpx 40rpx 36rpx;
  border-top: 1px solid #e5e7eb;
}
.modal-btn {
  background: #111827;
  color: #ffffff;
  text-align: center;
  padding: 24rpx;
  border-radius: 44rpx;
  font-size: 30rpx;
  font-weight: bold;
}
</style>
