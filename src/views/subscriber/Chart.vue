<!-- src/components/Chart.vue -->
<template>
    <div>
      <line-chart :data="chartData" :options="chartOptions" />
    </div>
  </template>
  
  <script>
  import { Line } from 'vue-chartjs';
  import { Chart as ChartJS, Title, Tooltip, Legend, LineElement, PointElement, CategoryScale, LinearScale } from 'chart.js';
  
  // Register the necessary chart.js components
  ChartJS.register(Title, Tooltip, Legend, LineElement, PointElement, CategoryScale, LinearScale);
  
  export default {
    name: 'Chart',
    components: {
      LineChart: Line
    },
    props: {
      temperatureData: Array,
      humidityData: Array,
      pressureData: Array
    },
    computed: {
      chartData() {
        return {
          labels: this.temperatureData.map((_, index) => `Time ${index + 1}`),
          datasets: [
            {
              label: '温度 (°C)',
              data: this.temperatureData,
              borderColor: 'rgb(255, 99, 132)',
              backgroundColor: 'rgba(255, 99, 132, 0.2)',
              fill: false
            },
            {
              label: '湿度 (%)',
              data: this.humidityData,
              borderColor: 'rgb(54, 162, 235)',
              backgroundColor: 'rgba(54, 162, 235, 0.2)',
              fill: false
            },
            {
              label: '气压 (hPa)',
              data: this.pressureData,
              borderColor: 'rgb(75, 192, 192)',
              backgroundColor: 'rgba(75, 192, 192, 0.2)',
              fill: false
            }
          ]
        };
      },
      chartOptions() {
        return {
          responsive: true,
          plugins: {
            title: {
              display: true,
              text: '温湿度气压变化趋势'
            },
            tooltip: {
              mode: 'index',
              intersect: false
            }
          }
        };
      }
    }
  };
  </script>
  