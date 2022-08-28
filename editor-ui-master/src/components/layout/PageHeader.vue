<template>
  <el-menu :default-active="activeIndex"
           class="el-menu-demo"
           background-color="#545c64"
           text-color="#fff"
           active-text-color="#ffd04b"
           mode="horizontal">
    <el-menu-item index="1">处理中心</el-menu-item>
    <el-menu-item index="2">我的工作台</el-menu-item>
    <el-menu-item index="3">消息中心</el-menu-item>
  </el-menu>
</template>

<script>
export default {
  name: "PageHeader",
  data() {
    return {
      activeIndex : '2',
    };
  },
}
</script>

<style scoped>

</style>
