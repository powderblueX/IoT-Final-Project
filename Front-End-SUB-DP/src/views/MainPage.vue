<script setup>
import router from "@/router/index.js";
import { onMounted, onUnmounted, reactive } from "vue";

// 定义逻辑
const roomsPosition = reactive({
  subscriber: { rotation: 0 }, // 每个按钮的初始旋转角度
  dataProcessor: { rotation: 0 },
});

const handleMouseMove = (event) => {
  const mouseX = event.clientX;
  const mouseY = event.clientY;

  document.querySelectorAll(".room").forEach((room) => {
    const rect = room.getBoundingClientRect();
    const roomX = rect.left + rect.width / 2;
    const roomY = rect.top + rect.height / 2;

    const distance = Math.sqrt(
      (mouseX - roomX) ** 2 + (mouseY - roomY) ** 2
    );
    const maxDistance = 300; // 定义影响范围
    const scale = Math.max(1, 1.5 - distance / maxDistance); // 计算缩放比例

    room.style.transform = `rotate(${roomsPosition[room.id].rotation}deg) scale(${scale})`;
    room.style.transition = "transform 0.1s ease"; // 增加平滑过渡
  });
};

onMounted(() => {
  document.addEventListener("mousemove", handleMouseMove);
});

onUnmounted(() => {
  document.removeEventListener("mousemove", handleMouseMove);
});
</script>

<template>
    <el-container>
        <router-view v-slot="{ Component }">
            <transition name="el-fade-in-linear" mode="out-in">
                <component :is="Component"/>
            </transition>
        </router-view>
    </el-container>
    <el-container class="footer-buttons">
        <el-main>
            <el-button type="info" class="room" id="subscriber" @click="router.push('/')" round size="large" > 订阅端 </el-button>
            <el-button type="primary" class="room" id="dataProcessor" @click="router.push('/dataProcessor')" round size="large" > 数据处理端 </el-button>
        </el-main>
    </el-container>
</template>


<style scoped>
.el-main {
    display: flex;
    justify-content: center;
    align-items: center;
}

.footer-buttons {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  border-radius: 10px 10px 0 0; 
  padding: 10px;
  z-index: 1000;
}

.footer-buttons .el-button {
  margin: 0 30px;
}

.footer-buttons .room {
  display: inline-block;
  transition: transform 0.2s ease, box-shadow 0.2s ease, background-color 0.2s ease;
  cursor: pointer;
  padding: 10px 20px; /* 可选：增加按钮内边距 */
  border-radius: 8px; /* 可选：按钮圆角 */
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1); /* 默认的边框阴影 */
}

.footer-buttons .room:hover {
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.2); /* 悬停时增强阴影 */
  transform: scale(1.1); /* 悬停时放大效果 */
}

.footer-buttons .room:active {
  transform: scale(0.95); /* 点击时缩小效果 */
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2); /* 点击时弱化阴影 */
}
</style>