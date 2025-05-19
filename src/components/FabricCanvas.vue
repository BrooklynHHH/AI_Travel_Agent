<template>
  <div class="fabric-modal-overlay">
    <div class="fabric-container">
      <div ref="canvasContainer" class="canvas-wrapper">
        <canvas ref="fabricCanvas"></canvas>
      </div>
      <div class="button-container">
        <button @click="confirmCrop" class="action-button">确认</button>
        <button @click="cancelCrop" class="action-button">取消</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, watch, nextTick, defineProps, defineEmits } from 'vue';

const props = defineProps({
  imageUrl: String, // 需要裁剪的图片
  visible: Boolean  // 控制显示
});
const emits = defineEmits(['confirm', 'cancel']);

const fabricCanvas = ref(null);
const canvasInstance = ref(null);
const rect = ref(null);
const imgObj = ref(null);

const canvasContainer = ref(null);

const confirmCrop = () => {
  if (!rect.value || !imgObj.value) return;
  
  // 获取选区坐标和尺寸（相对于画布）
  // 确保使用实际的宽高（考虑缩放因子）
  let box = {
    left: Math.round(rect.value.left),
    top: Math.round(rect.value.top),
    width: Math.round(rect.value.width * rect.value.scaleX),
    height: Math.round(rect.value.height * rect.value.scaleY),
    rx: rect.value.rx,
    ry: rect.value.ry
  };
  
  // 确保坐标和尺寸不超出画布范围
  if (canvasInstance.value) {
    const canvasWidth = canvasInstance.value.width;
    const canvasHeight = canvasInstance.value.height;
    
    // 确保left和top不小于0
    box.left = Math.max(0, box.left);
    box.top = Math.max(0, box.top);
    
    // 确保width和height不超出画布
    box.width = Math.min(canvasWidth - box.left, box.width);
    box.height = Math.min(canvasHeight - box.top, box.height);
  }
  
  // 计算图片的缩放比例
  const imgScaleX = imgObj.value.width / (imgObj.value.width * imgObj.value.scaleX);
  const imgScaleY = imgObj.value.height / (imgObj.value.height * imgObj.value.scaleY);
  
  // 将选区坐标和尺寸从画布坐标系转换为原始图片坐标系
  const originalBox = {
    left: Math.round(box.left * imgScaleX),
    top: Math.round(box.top * imgScaleY),
    width: Math.round(box.width * imgScaleX),
    height: Math.round(box.height * imgScaleY),
    rx: box.rx,
    ry: box.ry
  };
  
  console.log('画布裁剪区域:', box);
  console.log('原始图片裁剪区域:', originalBox);
  emits('confirm', originalBox);
};

const cancelCrop = () => {
  emits('cancel');
};

const loadFabric = () => {
  return new Promise(resolve => {
    if (window.fabric) {
      return resolve(window.fabric);
    }
    const script = document.createElement('script');
    script.src = 'https://cdnjs.cloudflare.com/ajax/libs/fabric.js/5.3.0/fabric.min.js';
    script.onload = () => {
      resolve(window.fabric);
    };
    document.head.appendChild(script);
  });
};

onMounted(() => {
  nextTick(() => {
    if (props.imageUrl) {
      loadFabric().then(() => {
        initFabric();
      });
    }
  });
});

// 定义一个初始化Fabric的函数
const initFabric = () => {
  if (!window.fabric) {
    console.error('fabric is not loaded');
    return;
  }
  const fabric = window.fabric;
  if (canvasInstance.value) {
    canvasInstance.value.dispose();
    canvasInstance.value = null;
  }
  // 获取容器宽高
  const container = canvasContainer.value;
  const width = container ? container.offsetWidth : 400;
  const height = container ? container.offsetHeight : 300;

  // 创建 fabric.Canvas
  canvasInstance.value = new fabric.Canvas(fabricCanvas.value, {
    width,
    height,
    selection: false,
    uniformScaling: false // 默认不保持比例缩放
  });

  // 加载图片
  fabric.Image.fromURL(props.imageUrl, (img) => {
    img.set({
      left: 0,
      top: 0,
      selectable: false,
      evented: false
    });
    // 缩放图片以适应画布
    img.scaleToWidth(width);
    img.scaleToHeight(height);
    canvasInstance.value.setBackgroundImage(img, canvasInstance.value.renderAll.bind(canvasInstance.value));
    imgObj.value = img;

    // 默认选区为全图
    if (rect.value) {
      canvasInstance.value.remove(rect.value);
    }
    // 设置初始矩形，与边缘有20像素的间隔
    const padding = 20;
    rect.value = new fabric.Rect({
      left: padding,
      top: padding,
      width: width - (padding * 2),
      height: height - (padding * 2),
      rx: 20,
      ry: 20,
      fill: 'rgba(0,0,0,0.1)',
      stroke: 'red',
      strokeWidth: 2,
      hasRotatingPoint: false,
      cornerColor: 'blue',
      transparentCorners: false,
      cornerSize: 10,
      lockRotation: true,
      lockSkewingX: true,
      lockSkewingY: true,
      lockMovementX: false, // 允许移动
      lockMovementY: false, // 允许移动
      centeredScaling: false,
      lockUniScaling: false, // 允许非等比例缩放
      lockScalingFlip: false, // 允许通过缩放翻转
      objectCaching: false,
      borderScaleFactor: 1
    });
    rect.value.setControlsVisibility({
      mtr: false // 隐藏旋转控件
    });
    canvasInstance.value.add(rect.value);
    canvasInstance.value.setActiveObject(rect.value);
    canvasInstance.value.renderAll();
  });
};

watch(() => props.imageUrl, (newVal) => {
  if (newVal) {
    nextTick(() => {
      loadFabric().then(() => {
        initFabric();
      });
    });
  }
});

// 监听visible属性变化，当显示时初始化canvas
watch(() => props.visible, (newVal) => {
  if (newVal && props.imageUrl) {
    nextTick(() => {
      loadFabric().then(() => {
        initFabric();
      });
    });
  }
});

onBeforeUnmount(() => {
  if (canvasInstance.value) {
    canvasInstance.value.dispose();
    canvasInstance.value = null;
  }
});
</script>

<style scoped>
.fabric-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background-color: rgba(0, 0, 0, 0.7);
  z-index: 1000;
  display: flex;
  justify-content: center;
  align-items: center;
}

.fabric-container {
  display: flex;
  flex-direction: column;
  background-color: white;
  border-radius: 8px;
  padding: 20px;
  width: 80%;
  max-width: 1000px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.button-container {
  display: flex;
  justify-content: center;
  margin-top: 20px;
  padding: 10px;
}

.action-button {
  padding: 10px 24px;
  margin: 0 10px;
  border-radius: 6px;
  border: 1px solid #ccc;
  background: #f7f7f7;
  cursor: pointer;
  font-size: 16px;
  font-weight: 500;
  transition: all 0.3s;
}

.action-button:hover {
  background: #e6f7ff;
  border-color: #1890ff;
  color: #1890ff;
}

.canvas-wrapper {
  position: relative;
  width: 100%;
  height: 70vh;
  display: flex;
  justify-content: center;
  align-items: center;
}

canvas {
  border: 1px solid #eee;
  background: #fff;
  width: 100%;
  height: 100%;
  display: block;
  margin: 0 auto;
}
</style>
