<template>
  <div class="settings-panel">
    <el-form label-position="top">
      <!-- 数据类型选择 -->
      <el-form-item label="数据类型">
        <el-radio-group v-model="localDataType">
          <el-radio-button label="temperature">温度</el-radio-button>
          <el-radio-button label="humidity">湿度</el-radio-button>
          <el-radio-button label="pressure">气压</el-radio-button>
        </el-radio-group>
      </el-form-item>

      <!-- 夜间模式切换 -->
      <el-form-item label="主题设置">
        <el-switch 
          v-model="darkMode" 
          active-text="夜间模式"
          inactive-text="白天模式"
          @change="toggleTheme" 
        />
      </el-form-item>
    </el-form>
  </div>
</template>

<script>
import { ref, watch } from 'vue';

export default {
  props: {
    modelValue: {
      type: String,
      required: true,
    },
    selectedTheme: {
      type: String,
      required: true,
    },
  },
  emits: ['update:modelValue', 'update:selectedTheme'], // 定义 emit 事件
  setup(props, { emit }) {
    const localDataType = ref(props.modelValue); // 本地变量绑定
    const darkMode = ref(false);

    // 同步父组件的值
    watch(localDataType, (newValue) => {
      console.log("SettingsPanel 数据类型变化:", newValue);
      emit('update:modelValue', newValue);
    });

    const toggleTheme = (value) => {
      emit('update:selectedTheme', value ? 'dark-theme' : '');
    };

    return { localDataType, darkMode, toggleTheme };
  },
};
</script>

<style scoped>
.settings-panel {
  padding: 20px;
  transition: background-color 0.3s, color 0.3s;
  border-radius: 10px;
}

.dark-theme .settings-panel{
  background-color: #494464d3;
  color: aliceblue;
}
</style>
