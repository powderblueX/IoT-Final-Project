<template>
  <el-table :data="filteredData" border style="width: 100%;">
    <el-table-column prop="time" label="时间" />
    <el-table-column :prop="dataType" :label="columnLabel" />
  </el-table>
</template>

<script>
import { computed } from "vue";

export default {
  props: {
    data: {
      type: Array,
      required: true,
    },
    dataType: {
      type: String,
      required: true,
    },
  },
  setup(props) {
    // 动态生成表头名称
    const columnLabel = computed(() => {
      switch (props.dataType) {
        case "temperature":
          return "温度 (°C)";
        case "humidity":
          return "湿度 (%)";
        case "pressure":
          return "气压 (hPa)";
        default:
          return "数据";
      }
    });

    // 格式化时间函数
    const formatTime = (timestamp) => {
      const date = new Date(timestamp);
      return new Intl.DateTimeFormat("zh-CN", {
        year: "numeric",
        month: "2-digit",
        day: "2-digit",
        hour: "2-digit",
        minute: "2-digit",
        second: "2-digit",
        hour12: false, // 24小时制
      }).format(date).replace(/\//g, "-"); // 替换/为-以符合目标格式
    };

    // 过滤出当前需要的数据，并格式化时间
    const filteredData = computed(() =>
      props.data.map((item) => ({
        time: formatTime(item.timestamp),
        [props.dataType]: item[props.dataType],
      }))
    );

    return { filteredData, columnLabel };
  },
};
</script>

<style scoped>
  
</style>
