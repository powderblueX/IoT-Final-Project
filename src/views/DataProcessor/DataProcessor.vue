<template>
  <el-container>
    <!-- 顶部标题 -->
    <el-header class="header-container animated fade-in">
      <div class="header-content">
        <img src="../../assets/logo.png" alt="Logo" class="logo" />
        <span class="header-title">MQTT 数据处理分析展示</span>
      </div>
    </el-header>

    <!-- 主体内容 -->
    <el-main class="main-content">
      <!-- 简介 -->
      <el-card shadow="hover" style="margin-bottom: 20px;">
        <template #header>
          <span style="font-size: xx-large; font-family: KaiTi; font-weight: bolder;">系统简介</span>
        </template>
        <p style="font-size: large; font-family: KaiTi; ">
          该系统旨在实时订阅和展示 MQTT 数据，支持多种传感器类型的数据处理和分析。
          用户可以得到处理后的模拟分析预测数据曲线与历史数据曲线。
          用户可以查看到传感器在哪些时刻没有正常工作。
          用户可以通过滑块调整显示的数据点数量，同时可保存数据以供后续分析。
        </p>
      </el-card>

      <!-- 控制区域 -->
      <div class="controls-container">
        <div class="form-container">
          <el-select
            v-model="sensorType"
            placeholder="请选择传感器类型"
            @change="fetchAndRenderData"
          >
            <el-option label="温度" value="temperature"></el-option>
            <el-option label="湿度" value="humidity"></el-option>
            <el-option label="气压" value="pressure"></el-option>
          </el-select>
        </div>
        <div class="slider-container">
          <div>
            历史数据点数
            <el-slider
              v-model="historyCount"
              :min="1"
              :max="1000"
              :step="1"
              tooltip-class="custom-tooltip"
              show-input
              input-size="mini"
              label="历史数据点数"
            ></el-slider>
          </div>
          <div>
            预测数据点数
            <el-slider
              v-model="predictionCount"
              :min="1"
              :max="1000"
              :step="1"
              tooltip-class="custom-tooltip"
              show-input
              input-size="mini"
              label="预测数据点数"
            ></el-slider>
          </div>
        </div>
      </div>

      <!-- 图表区域 -->
      <div class="content-container">
        <div class="chart-container">
          <line-chart v-if="datacollection" :data="datacollection" :options="options"></line-chart>
        </div>
      </div>

      <!-- 保存数据按钮 -->
      <el-row justify="center" style="margin-top: 20px;">
        <el-button type="success" size="large" @click="saveData">
          保存数据
        </el-button>
      </el-row>

      <!-- 异常信息卡片 -->
      <el-card shadow="hover" style="margin-top: 20px;">
        <template #header>
          <span>传感器异常记录</span>
        </template>
        <el-table :data="anomalies" border style="width: 100%;">
          <el-table-column prop="timestamp" label="时间" width="200" />
          <el-table-column prop="sensorType" label="传感器类型" width="150" />
          <el-table-column prop="reason" label="异常原因" />
        </el-table>
      </el-card>
    </el-main>
  </el-container>
</template>

<script>
import { ref, watch, onMounted } from "vue";
import { Line } from "vue-chartjs";
import {
  Chart as ChartJS,
  Title,
  Tooltip,
  Legend,
  LineElement,
  LinearScale,
  CategoryScale,
  PointElement,
  TimeScale,
} from "chart.js";
import ChartDataLabels from "chartjs-plugin-datalabels";
import "chartjs-adapter-date-fns";

ChartJS.register(
  Title,
  Tooltip,
  Legend,
  LineElement,
  LinearScale,
  CategoryScale,
  PointElement,
  TimeScale,
  ChartDataLabels
);

export default {
  components: {
    LineChart: Line,
  },
  setup() {
    const sensorType = ref("temperature");
    const datacollection = ref(null);
    const anomalies = ref([]); // 异常记录

    const options = ref({
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        x: {
          type: "time",
          time: {
            unit: "hour",
            tooltipFormat: "yyyy-MM-dd HH:mm",
            displayFormats: {
              minute: "HH:mm",
            },
          },
          adapters: {
            date: {
              timeZone: "Asia/Shanghai",
            },
          },
          title: {
            display: true,
            text: "时间",
          },
        },
        y: {
          title: {
            display: true,
            text: "数值",
          },
        },
      },
      plugins: {
        datalabels: {
          display: false,
        },
        legend: {
          position: "top",
        },
        title: {
          display: true,
          text: sensorType.value,
        },
      },
    });

    const historyCount = ref(9);
    const predictionCount = ref(18);

    const fetchAndRenderData = async () => {
      const apiUrl = `http://192.168.37.91:5000/api/get_predictions?topic=sensor/${sensorType.value}`;
      try {
        const response = await fetch(apiUrl);
        if (!response.ok) {
          throw new Error(`HTTP 错误！状态码: ${response.status}`);
        }
        const data = await response.json();
        console.log(data)

        const detectedAnomalies = [];

        //遍历数据并分类
        data.forEach((item) => {
          if (item.actual_value == null && item.predicted_value != null) {
            // 没有历史数据但有预测值，判断为异常
            detectedAnomalies.push({
              timestamp: item.timestamp,
              sensorType: sensorType.value,
              reason: `没有对应的历史数据`,
            });
          }
        });

        // 更新异常和图表数据
        anomalies.value = detectedAnomalies;

        // 数据处理逻辑
        const historicalDataset = data
          .slice(-historyCount.value - 9)
          .map((item) => ({
            x: item.timestamp,
            y: item.actual_value,
          }));

        const predictedDataset = data
          .slice(-predictionCount.value)
          .map((item) => ({
            x: item.timestamp,
            y: item.predicted_value,
          }));

        // // 检查异常
        // const historicalTimestamps = new Set(
        //   historicalDataset.map((item) => item.x)
        // );
        // const detectedAnomalies = predictedDataset
        //   .filter((item) => !historicalTimestamps.has(item.x))
        //   .map((item) => ({
        //     timestamp: item.x,
        //     sensorType: sensorType.value,
        //     reason: `没有对应的历史数据`,
        //   }));

        // anomalies.value = detectedAnomalies;

        datacollection.value = {
          datasets: [
            {
              label: "历史数据",
              borderColor: "#FF0000",
              backgroundColor: "rgba(255, 0, 0, 0.2)",
              data: historicalDataset,
              fill: false,
              tension: 0.1,
            },
            {
              label: "预测数据",
              borderColor: "#0000FF",
              backgroundColor: "rgba(0, 0, 255, 0.2)",
              data: predictedDataset,
              fill: false,
              tension: 0.1,
            },
          ],
        };
      } catch (error) {
        console.error("数据获取失败:", error);
        alert("无法连接到后端服务，请检查网络或联系管理员。");
      }
    };

    // 保存数据功能
    const saveData = () => {
      if (!datacollection.value) {
        alert("没有数据可保存！");
        return;
      }
      const dataToSave = JSON.stringify(datacollection.value, null, 2);
      const blob = new Blob([dataToSave], { type: "application/json" });
      const link = document.createElement("a");
      link.href = URL.createObjectURL(blob);
      link.download = "data.json";
      link.click();
    };

    watch([historyCount, predictionCount], fetchAndRenderData);
    onMounted(fetchAndRenderData);

    return {
      sensorType,
      datacollection,
      options,
      anomalies,
      historyCount,
      predictionCount,
      fetchAndRenderData,
      saveData,
    };
  },
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

.main-content {
  padding: 20px;
}

.controls-container {
  display: flex;
  justify-content: space-between;
  margin-bottom: 20px;
}

.form-container {
  width: 200px;
}

.slider-container {
  display: flex;
  gap: 50px;
  align-items: center;
}

.content-container {
  display: flex;
  gap: 20px;
  margin-top: 20px;
}

.chart-container {
  flex: 1;
  width: 100%;
  min-width: 300px;
  min-height: 300px;
}
</style>
