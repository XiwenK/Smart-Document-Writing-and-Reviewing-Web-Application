<template>
<div>
  <div style="width: border-box">
    <PageHeader></PageHeader>
  </div>

  <div style="margin-top: 20px">
    <el-row>
      <el-col :span="2">
        <el-row style="margin-top: 20px; margin-bottom: 15px">
          <el-button type="primary" id="flowBttn" :disabled="disabled" @click="handleGenerate()">智能生成</el-button>
        </el-row>
        <el-row>
          <el-input type="textarea" v-model="textGen" placeholder="在此处查看生成文本" :rows="10"></el-input>
        </el-row>
      </el-col>

      <el-col :span="16" :offset="1">
        <el-card>

          <el-row style="margin-bottom: 15px">
            <el-upload
              action="http://localhost:8081/upload/word/template"
              :on-success="handleSuccess"
              :show-file-list="false"
              class="inline-block"
              style="margin-right: 10px">
              <el-button>导入模板</el-button>
            </el-upload>
            <el-button type="ghost" @click="handleSubmit()">导出文本</el-button>
            <el-button type="ghost" @click="handleReset()">清空文本</el-button>
          </el-row>

          <el-form ref="editorModel" :model="editorModel" :rules="editorRules">
            <el-form-item prop="content">
              <el-input type="textarea"  class='tinymce-textarea' id="tinymceEditor" v-model="editorModel.content" style="height: 1000px">
              </el-input>
            </el-form-item>
          </el-form>

        </el-card>
      </el-col>

      <el-col :span="2" :offset="1">
        <el-row style="margin-top: 20px; margin-bottom: 15px; margin-left: 45px">
          <el-button type="primary" @click="handleCorrect()">文本纠错</el-button>
        </el-row>
        <el-row>
          <el-input type="textarea" v-model="textCorrect" placeholder="在此处查看错误文本" :rows="10" style="width: 220px"></el-input>
        </el-row>
      </el-col>
    </el-row>
  </div>
</div>
</template>

<script>
import tinymce from 'tinymce';
import util from '../libs/util';
import textUtil from "../libs/textUtil";
import PageHeader from '../components/layout/PageHeader'

export default {
  name: 'home',
  components: {PageHeader},
  data () {
    return {
      editorModel: {
        content: ""
      },
      textModel: {
        content: ""
      },
      correctModel: {
        content: ""
      },
      editorRules: {
        content: [
          {
            type: 'string',
            min: 5,
            message: 'the username size shall be no less than 5 chars ',
            trigger: 'blur'
          }
        ]
      },
      textGen:"",
      textCorrect: "",
      customEditor: null,
      disabled: true,
    };
  },
  methods: {
    init () {
      this.$nextTick(() => {
        let vm = this
        let height = document.body.offsetHeight - 300;
        tinymce.init({
          selector: '#tinymceEditor',
          // inline: true,
          branding: false,
          elementpath: false,
          height: height,
          language: 'zh_CN.GB2312',
          menubar: 'edit insert view format table tools',
          plugins: [
            'advlist autolink lists link image charmap print preview hr anchor pagebreak imagetools',
            'searchreplace visualblocks visualchars code fullpage',
            'insertdatetime media nonbreaking save table contextmenu directionality',
            'emoticons paste textcolor colorpicker textpattern imagetools codesample'
          ],
          toolbar1: ' newnote print preview | undo redo | insert | styleselect | forecolor backcolor bold italic | alignleft aligncenter alignright alignjustify | bullist numlist outdent indent | link image emoticons media codesample',
          autosave_interval: '20s',
          image_advtab: true,
          image_upload_base_path: '/Users/seanking/Desktop/editor-service-master/pic',
          table_default_styles: {
            width: '100%',
            height: '100%',
            borderCollapse: 'collapse'
          },
          setup: function (editor) {
            editor.on('change',function(){
              editor.save();
              // console.log(document.getElementById('tinymceEditor').value);
            });

            // editor.on('keydown', function (e) {
            //   console.log(localStorage.editorContent);
            //   localStorage.editorContent = tinymce.get('tinymceEditor').getContent();
            //   vm.editorModel.content = tinymce.get('tinymceEditor').getContent();
            //   console.log("new content is : ")
            //   console.log(localStorage.editorContent);
            // });

            editor.on('keyup', function (e) {
              localStorage.editorContent = tinymce.get('tinymceEditor').getContent();
              vm.editorModel.content = tinymce.get('tinymceEditor').getContent();
            });

            editor.on('mouseup', function (e) {
              let text = tinymce.activeEditor.selection.getContent({'format':'text'});
              vm.disabled = true;
              if (text !== '') {
                vm.disabled = false;
                vm.textModel.content = text;
              }
            });
          }
        });
      });
    },
    handleSuccess(res){
      this.customEditor = res.content;

      this.editorModel['content'] = res.content;
      tinymce.get('tinymceEditor').setContent(this.customEditor);

      let activeEditor = tinymce.activeEditor;
      let editBody = activeEditor.getBody();
      activeEditor.selection.select(editBody);
      this.correctModel['content'] = activeEditor.selection.getContent({'format': 'text'});

      this.$message.success("上传成功");
    },
    handleSubmit () {
      this.$refs.editorModel.validate((valid) => {
        if (valid) {
          util.post('/html/pdf', this.editorModel).then(res => {
            this.$message.success("导出成功");
          });
        } else {
          this.$message.error('导出失败');
        }
      });
    },
    handleReset () {
      tinymce.get('tinymceEditor').setContent("");
    },
    handleGenerate () {
      textUtil.post('/textGen', this.textModel).then(res => {
        this.textGen = res.data['text'];
        // console.log(this.textGen);
        // alert(this.textGen);
        this.$message.success("生成成功");
      });
      this.disabled = true;
    },
    handleCorrect () {
      let activeEditor = tinymce.activeEditor;
      let editBody = activeEditor.getBody();
      activeEditor.selection.select(editBody);
      this.correctModel['content'] = activeEditor.selection.getContent({'format': 'text'});

      textUtil.post('/textCorrect', this.correctModel).then(res =>{
        this.textCorrect = res.data['resultList']

        this.$message.success("检测成功");
      });
    }
  },
  mounted () {
    this.init();
  },
  destroyed () {
    tinymce.get('tinymceEditor').destroy();
  }
}
</script>

<style>
.inline-block {
  display: inline-block;
}
</style>
