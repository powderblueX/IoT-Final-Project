<template>
  <div>
    <canvas ref="chartCanvas" width="400" height="200"></canvas>
  </div>
</template>

<script>
import { ref, watch, onMounted, onBeforeUnmount } from "vue";
import Chart from "chart.js/auto";
import 'chartjs-adapter-date-fns';  // 引入时间适配器

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
    const chartCanvas = ref(null); // canvas 引用
    let chartInstance = null;

    // 设置不同数据类型的颜色
    const getBorderColor = (dataType) => {
      switch (dataType) {
        case "temperature":
          return "#ff5733"; // 温度的颜色
        case "humidity":
          return "#33ccff"; // 湿度的颜色
        case "pressure":
          return "#4caf50"; // 气压的颜色
        default:
          return "#409eff";
      }
    };

    // 更新图表数据
    const updateChart = () => {
      console.log("图表更新:", props.dataType);
      const labels = props.data.map((item) => item.timestamp);
      
      // 根据 dataType 动态选择温度或湿度的数据
      const dataValues = props.data.map((item) => {
        if (props.dataType === "humidity") {
          return item.humidity;
        } else if (props.dataType === "pressure") {
          return item.pressure;
        }
        return item.temperature;
      });

      if (chartInstance) {        
        chartInstance.data.labels = labels;
        chartInstance.data.datasets[0].data = dataValues;
        chartInstance.data.datasets[0].label = props.dataType; // 更新图表标题
        chartInstance.data.datasets[0].borderColor = getBorderColor(props.dataType); // 动态更新颜色
        chartInstance.data.datasets[0].backgroundColor = getBorderColor(props.dataType).replace("1)", "0.2)"); // 修改背景色透明度
        chartInstance.update();
      }
    };
    
    // 初始化图表
    const initializeChart = () => {
      const labels = props.data.map((item) => new Date(item.timestamp)); // 转换时间为 Date 对象
      const dataValues = props.data.map((item) => {
        if (props.dataType === "humidity") {
          return item.humidity;
        } else if (props.dataType === "pressure") {
          return item.pressure;
        }
        return item.temperature;
      });

      chartInstance = new Chart(chartCanvas.value, {
        type: "line",
        data: {
          labels,
          datasets: [
            {
              label: props.dataType,
              data: dataValues,
              borderColor: getBorderColor(props.dataType),
              backgroundColor: getBorderColor(props.dataType).replace("1)", "0.2)"),
              fill: false,
              tension: 0.1,
            },
          ],
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            x: {
              type: "time", // 设置为时间类型
              time: {
                unit: "minute", // 时间单位为分钟
                tooltipFormat: "yyyy-MM-dd HH:mm", // 格式化时间
                displayFormats: {
                  minute: "HH:mm",
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
                text: `${props.dataType} 数据`,
              },
            },
          },
        },
      });
    };

    onMounted(() => {
      initializeChart();  // 初始化图表
    });

    // 调试，检查 props.data 和 props.dataType 是否正确传递
    watch(() => props.data, (newValue) => {
      console.log("Data updated:", newValue);
    });

    watch(() => props.dataType, (newValue) => {
      console.log("Data type updated:", newValue);
    });

    // 监听数据变化，更新图表
    watch(() => props.data, updateChart, { deep: true, immediate: true }); // { immediate: true } 确保初始数据也会更新图表
    watch(() => props.dataType, updateChart); // 监听数据类型变化，更新图表

    // 清理图表实例，避免内存泄漏
    onBeforeUnmount(() => {
      if (chartInstance) {
        chartInstance.destroy();
      }
    });

    return { chartCanvas };
  },
};
</script>
