<template>
  <el-container :class="[selectedTheme]" style="min-height: 100vh;">
    <!-- 顶部标题 -->
    
    <el-header class="header-container animated fade-in">
      <div class="header-content">
        <img src="../../assets/logo.png" alt="Logo" class="logo" />
        <span class="header-title">MQTT 实时数据订阅与展示</span>
        <!-- <el-tag :type="connectionStatus" class="status-tag">{{ connectionStatusText }}</el-tag> -->
      </div>
    </el-header>


    <!-- 主体内容 -->
    <el-main>
      <el-row :gutter="20">
        <el-col :span="6">
          <el-card shadow="hover" style="margin-bottom: 20px;">
            <template #header>
              <span style="font-size: xx-large; font-family: KaiTi; font-weight: bolder;">系统简介</span>
            </template>
            <p style="font-size: large; font-family: KaiTi; ">
              该系统用于实时订阅和展示 MQTT 数据，可切换不同的数据类型并支持主题设置。
              用户可以通过右侧的图表和表格实时查看数据变化，还可以导出数据以便分析。
            </p>
          </el-card>
          <!-- 左侧设置面板 -->
          <el-col :span="30">
            <el-card shadow="hover" >
              <settings-panel
                v-model:modelValue="dataType" 
                v-model:selectedTheme="selectedTheme" 
              />
            </el-card>
          </el-col>
          <el-card shadow="hover" style="margin-top: 20px;">
            <img
              src="@/assets/image.png"
              alt="MQTT 某区域温度/湿度/气压数据"
              style="width: 100%; height: auto; object-fit: contain; " 
            />
          </el-card>
        </el-col>
        <!-- 右侧展示区域 -->
        <el-col :span="18">
          <!-- 数据折线图 -->
          <el-card shadow="hover" style="margin-bottom: 20px;">
            <data-chart :data="chartData" :dataType="dataType" />
          </el-card>

          <!-- 数据表格 -->
          <el-card shadow="hover">
            <data-table :data="chartData" :dataType="dataType" />
          </el-card>

          <!-- 数据导出按钮 -->
          <el-row justify="center" style="margin-top: 20px;">
            <el-button type="success" size="large" @click="exportData">
              导出数据
            </el-button>
          </el-row>
        </el-col>
      </el-row>
    </el-main>
  </el-container>
</template>

<script>
import { ref, watch, onMounted } from 'vue';
import mqtt from 'mqtt'
import SettingsPanel from './SettingsPanel.vue';
import DataChart from './DataChart.vue';
import DataTable from './DataTable.vue';

export default {
  components: { SettingsPanel, DataChart, DataTable },
  name: 'MqttChart',

  setup() {
    const selectedTheme = ref(""); // 主题切换 (默认白色)
    const dataType = ref("temperature"); // 数据类型切换，默认显示温度
    const chartData = ref([]); // 初始化 chartData

    // 获取最新数据的函数
    const fetchLatestData = async () => {
      try {
        const response = await fetch('http://127.0.0.1:5001/get-latest-data');
        const data = await response.json();
        chartData.value = data; // 更新图表数据
      } catch (error) {
        console.error('Error fetching data:', error);
      }
    };

    // 初始化时调用数据获取
    onMounted(() => {
      fetchLatestData();
    });

    // 监听数据类型变化
    watch(dataType, (newValue) => {
      console.log("父组件接收到的新数据类型:", newValue);
    });

    // 导出数据功能（暂时未实现）
    const exportData = () => {
      if (chartData.value.length === 0) {
        alert("没有可导出的数据！");
        return;
      }

      // 根据 dataType 动态选择字段
      const headers = ["时间", dataType.value];
      const rows = chartData.value.map((item) => [
        item.timestamp, // 时间戳
        item[dataType.value], // 动态选择数据类型列，例如 temperature, humidity
      ]);

      const csvContent = [headers.join(","), ...rows.map((row) => row.join(","))].join("\n");

      const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
      const link = document.createElement("a");
      const url = URL.createObjectURL(blob);

      link.setAttribute("href", url);
      link.setAttribute("download", `data_${dataType.value}.csv`);
      link.style.visibility = "hidden";
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    };

    return { selectedTheme, dataType, chartData, exportData };
  }
};
</script>

<style scoped>
.header-container {
  background-color: #386aaa;
  color: #ffffff;
  padding: 0 20px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  line-height: 60px;
}

.header-content {
  display: flex;
  align-items: center;
  gap: 15px;
}

.logo {
  width: 40px;
  height: 40px;
}

.header-title {
  font-size: 20px;
  font-weight: bold;
}

/* 暗黑主题 */
.dark-theme {
  background-color: #303133;
  color: white; /* 设置字体为白色 */
}

/* 暗黑模式的标题、段落和文字 */
.dark-theme .el-header,
.dark-theme .el-main,
.dark-theme p,
.dark-theme span,
.dark-theme .header-title {
  color: white !important;
}

/* 卡片内文字 */
.dark-theme .el-card {
  background-color: #424242 !important;
  color: white !important;
}

/* 卡片标题的特殊样式 */
.dark-theme .el-card__header {
  color: white !important;
}

/* 按钮文字颜色 */
.dark-theme .el-button {
  color: white !important;
}



.logo {
  width: 40px;
  height: 40px;
}
</style>
