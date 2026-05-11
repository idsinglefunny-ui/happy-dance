<template>
  <van-config-provider theme="light">
    <van-nav-bar title="莎莎总管后台" />
    <van-tabs v-model:active="activeTab" sticky>
      <van-tab title="认领审核">
        <div class="content">
          <div v-if="claims.length === 0" class="empty">暂无待审核申请</div>
          <van-card
            v-for="claim in claims"
            :key="claim.id"
            :desc="`申请人：${claim.applicant_name} (${claim.relationship})`"
            :title="claim.venue_name"
            :thumb="'https://via.placeholder.com/100x100/e5007f/fff?text=License'"
          >
            <template #tags>
              <van-tag plain type="primary">{{ claim.city }}</van-tag>
              <van-tag plain type="success" style="margin-left: 5px">{{ claim.contact_phone }}</van-tag>
            </template>
            <template #footer>
              <van-button size="small" type="danger" @click="reject(claim.id)">驳回</van-button>
              <van-button size="small" type="primary" @click="approve(claim.id)">通过</van-button>
            </template>
          </van-card>
        </div>
      </van-tab>
      <van-tab title="系统工具">
        <div class="content tools">
          <van-cell-group inset>
            <van-cell title="触发数据同步" label="手动触发Python抓取引擎">
              <template #right-icon>
                <van-button size="small" type="primary" :loading="syncing" @click="triggerSync">立即执行</van-button>
              </template>
            </van-cell>
          </van-cell-group>
        </div>
      </van-tab>
    </van-tabs>
  </van-config-provider>
</template>

<script setup>
import { ref } from 'vue';
import { showToast, showDialog } from 'vant';
import axios from 'axios';

const activeTab = ref(0);
const claims = ref([
  // 本地 Mock 数据，展示界面效果
  { id: 1, venue_name: "成都星海壹号", city: "成都市", applicant_name: "张总", relationship: "老板", contact_phone: "13800001111" }
]);
const syncing = ref(false);

const approve = (id) => {
  showDialog({ title: '确认', message: '确认审核通过该认领申请？' }).then(() => {
    showToast('已通过');
    claims.value = claims.value.filter(c => c.id !== id);
  });
};

const reject = (id) => {
  showToast('已驳回');
  claims.value = claims.value.filter(c => c.id !== id);
};

const triggerSync = async () => {
  syncing.value = true;
  try {
    const res = await axios.post('/api/admin/trigger-sync');
    if (res.data && res.data.code === 200) {
      showToast(`同步成功: 更新了 ${res.data.data.synced_count} 家舞厅`);
    } else {
      showToast('同步异常');
    }
  } catch (error) {
    showToast('网络请求失败，请确保 FastAPI 后端已启动');
  } finally {
    syncing.value = false;
  }
};
</script>

<style>
body { background-color: #f7f8fa; margin: 0; }
.content { padding: 16px 0; }
.tools { padding: 16px; }
.empty { text-align: center; color: #999; padding: 40px; }
</style>
