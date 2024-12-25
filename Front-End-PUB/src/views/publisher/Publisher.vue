<template>
  <el-container>
    <!-- 顶部导航 -->
    <el-header class="header-container animated fade-in">
      <div class="header-content">
        <img src="../../assets/logo.png" alt="Logo" class="logo" />
        <span class="header-title">MQTT 数据发布端</span>
        <el-tag :type="connectionStatus" class="status-tag">{{ connectionStatusText }}</el-tag>
      </div>
    </el-header>

    <el-main>
      <el-row :gutter="20">
        <!-- 说明区域 -->
        <el-col :span="24">
          <el-card class="info-card hover-effect animated slide-in-left">
            <p>本系统通过 MQTT 协议发布来自三种传感器的数据：</p>
            <ul>
              <li>温度传感器：实时监测环境温度</li>
              <li>湿度传感器：实时监测空气湿度</li>
              <li>压力传感器：实时监测大气压强</li>
            </ul>
            <p>数据采集时间为每小时的 <strong>0分、20分、50分</strong>，并通过 MQTT Broker 发布。</p>
          </el-card>
        </el-col>

        <!-- 数据预览 -->
        <el-col :span="14">
          <el-card class="data-card hover-effect animated slide-in-up">
            <div slot="header" class="card-header data-preview-header hover-header">
              <span>数据预览</span>
            </div>
            <el-table
              :data="receivedData"
              border
              style="width: 100%"
              class="custom-table hover-table"
              @row-class-name="highlightNewData"
            >
              <el-table-column prop="timestamp" label="发布时间" width="200"></el-table-column>
              <el-table-column prop="message.timestamp" label="采集时间" width="200"></el-table-column>
              <el-table-column prop="message.temperature" label="温度 (°C)" width="120"></el-table-column>
              <el-table-column prop="message.humidity" label="湿度 (%)" width="120"></el-table-column>
              <el-table-column prop="message.pressure" label="气压 (hPa)" width="120"></el-table-column>
              <el-table-column prop="topic" label="主题"></el-table-column>
            </el-table>
          </el-card>
        </el-col>

        <!-- 日志 -->
        <el-col :span="10">
          <el-card class="log-card hover-effect animated slide-in-up">
            <div slot="header" class="card-header log-header hover-header">
              <span>日志</span>
            </div>
            <el-input
              type="textarea"
              :rows="10"
              v-model="log"
              readonly
              class="log-input hover-input"
            ></el-input>
          </el-card>
        </el-col>
      </el-row>
    </el-main>
  </el-container>
</template>

<script>
import { ElMessage } from 'element-plus';
import { io } from 'socket.io-client';
export default {
  data() {
    return {
      receivedData: [], // 存储接收到的所有数据
      log: '', // 日志
      connectionStatus: 'info', // WebSocket 连接状态
      connectionStatusText: 'Disconnected', // 连接状态文本
      socket: null, // WebSocket 客户端实例
      highlightedRows: new Set(), // 用于高亮新数据的行
    };
  },
  mounted() {
    this.initWebSocket();
  },
  methods: {
    // 初始化 WebSocket
    initWebSocket() {
      this.socket = io('http://127.0.0.1:5000'); // 替换为你的后端地址和端口

      this.socket.on('connect', () => {
        console.log('Connected to WebSocket');
        this.connectionStatus = 'success';
        this.connectionStatusText = 'Connected';
        this.log += 'WebSocket 已连接\n';
      });

      this.socket.on('new_message', (data) => {
        console.log('Received data:', data);
        this.receivedData.push(data); // 将完整数据推送到表格中

        // 添加新数据高亮逻辑
        this.highlightedRows.add(this.receivedData.length - 1);
        setTimeout(() => this.highlightedRows.delete(this.receivedData.length - 1), 2000);

        this.log += `接收到新数据: ${JSON.stringify(data)}\n`;
      });

      this.socket.on('disconnect', () => {
        console.warn('WebSocket disconnected');
        this.connectionStatus = 'danger';
        this.connectionStatusText = 'Disconnected';
        this.log += 'WebSocket 连接已断开\n';
      });

      this.socket.on('connect_error', (error) => {
        console.error('WebSocket connection error:', error);
        ElMessage.error('WebSocket 连接失败');
        this.connectionStatus = 'danger';
        this.connectionStatusText = 'Connection Failed';
      });
    },

    // 高亮新数据的行
    highlightNewData(row, rowIndex) {
      return this.highlightedRows.has(rowIndex) ? 'highlight-row' : '';
    },
  },
};
</script>

<style scoped>
/* 顶部导航样式 */
.header-container {
  background-color: rgba(56, 106, 170, 0.9);
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

.status-tag {
  font-size: 14px;
}

/* 卡片样式 */
.info-card,
.data-card,
.log-card {
  margin-bottom: 20px;
  border-radius: 10px;
  box-shadow: 0px 3px 8px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.hover-effect:hover {
  transform: translateY(-5px);
  box-shadow: 0px 6px 12px rgba(0, 0, 0, 0.2);
}

/* 说明区域 */
.info-card {
  background-color: rgba(255, 255, 255, 0.8);
  padding: 20px;
  border-left: 5px solid #386aaa;
}

/* 数据预览标题悬停 */
.hover-header:hover {
  color: #386aaa;
  font-size: 19px;
  transition: color 0.3s, font-size 0.3s;
}

/* 表格悬停效果 */
.hover-table .el-table__row:hover {
  background-color: #f1f7ff !important;
}

/* 日志区域 */
.log-input {
  font-family: monospace;
  background-color: #f7f9fc;
  border-radius: 5px;
  border: 1px solid #dfe6ed;
  color: #333;
  padding: 10px;
  resize: none;
  transition: border-color 0.3s;
}

.hover-input:hover {
  border-color: #386aaa;
}

/* 动态背景样式 */
.el-main {
  position: relative;
  z-index: 1;
  background: linear-gradient(135deg, #ffffff, #f8f9fa);
  height: 91vh; /* 全屏高度 */
  overflow: hidden;
}

/* 动态点效果 */
.el-main::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: radial-gradient(circle, rgba(200, 200, 200, 0.2) 2px, transparent 2px),
    radial-gradient(circle, rgba(240, 240, 240, 0.2) 1px, transparent 1px);
  background-size: 40px 40px, 80px 80px;
  animation: FlowingDots 10s linear infinite;
  z-index: -1;
}

/* 动态线条效果 */
.el-main::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, rgba(200, 200, 200, 0.1) 0%, rgba(200, 200, 200, 0.05) 50%, rgba(200, 200, 200, 0.1) 100%);
  background-size: 200% 200%;
  animation: FlowingLines 15s linear infinite;
  z-index: -2;
}

/* 动态点动画 */
@keyframes FlowingDots {
  0% {
    background-position: 0 0, 0 0;
  }
  100% {
    background-position: 50px 50px, -50px -50px;
  }
}

/* 动态线条动画 */
@keyframes FlowingLines {
  0% {
    background-position: 0% 50%;
  }
  50% {
    background-position: 100% 50%;
  }
  100% {
    background-position: 0% 50%;
  }
}
</style>
