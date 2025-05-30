<template>
  <div :class="needMinHeight?'msgContainer needPaddingBottom':'msgContainer'"
  :style="{ minHeight: needMinHeight ? mHeight : '0px'}"
  >
    <template v-if="conversationData.user.content">
      <div class="questions-box">
        <div class="questions">{{ conversationData.user.content }}</div>
      </div>
    </template>
    <div class="answerBox" v-answerExposeTrack_browser="{param:conversationData, extraParam: {ai_session_id: sessionId,ai_source: source}, rootMargin: `0px 0px -${inputHeights} 0px`}">
      <div class="loadingBox" v-if="conversationData.robot.content === '' && !conversationData.robot.errorMsg && conversationData.robot.streamingDeepThinkText === ''">
        <div v-if="!conversationData.robot.needPause">
          <div class="loadingTip">
            <span class="text-loading">
              <span v-if="currentChoosenStatus === '1'">深度思考中</span>
              <span v-if="currentChoosenStatus === '2'">正在检索参考资料</span>
              <span v-if="currentChoosenStatus === '3'">正在检索参考资料</span>
              <span v-if="currentChoosenStatus === '4'">正在为您进行回答</span>
            </span>
          </div>
        </div>
        <div v-else class="pause_step">已停止生成</div>
      </div>
      <div class="answers" ref="answers">
        <template v-if="(conversationData.robot.content !== '' || conversationData.robot.streamingDeepThinkText!== '') && !conversationData.robot.errorMsg">
          <div>
            <div class="answer-top" v-if="referenceNumber_used || referenceNumber_all || (conversationData.user.isDeepSearch && !(!deepThinkContent && mkHtml))">
              <div class="quote" v-if="referenceNumber_all && !referenceNumber_used">
                <div class="quote-title" @click="handleClick_quote">
                  <span>找到{{ referenceNumber_all }}篇参考资料</span>
                </div>
              </div>
              <div class="quote" v-if="referenceNumber_used">
                <div class="quote-title" @click="handleClick_quote">
                  <span>引用{{ referenceNumber_used }}篇资料作为参考</span>
                  <span>
                    <template v-for = '(item,index) in showImgs' :key="index">
                      <img :src="item?item:defaultQuoteIcon" alt="" @error="handlErrorImg" class="quoteIcon-title">
                    </template>
                  </span>
                </div>
                <div :class="conversationData.robot.showQuote?'quote-detail':'quote-detail quote-detail-hidden'"
                  @transitionend="transitionEnd" ref="quoteDetailRef">
                  <div v-for="(item, index) in JSON.parse(conversationData.robot.referenceData)"
                    @click="handleGoWebSite(item.url)" :key="index">
                    <img class="quoteIcon" :src="item.icon ? item.icon : defaultQuoteIcon" alt="" @error="handlErrorImg">
                    <span v-if="JSON.parse(conversationData.robot.referenceData).length>1">{{ index+1 }}. </span>
                    <span>{{ item.title }}</span>
                  </div>
                </div>
              </div>
              <div :class="((referenceNumber_all && !referenceNumber_used) || referenceNumber_used)?'deepThinkContentBox':'deepThinkContentBox needp'" v-if="conversationData.user.isDeepSearch && !(!deepThinkContent && mkHtml)">
                  <div class="thinkTitle" @click="handleClick_showdeepThink">
                    <div>
                      <span v-if="conversationData.robot.content===''">深度思考中</span>
                      <span v-if="conversationData.robot.content">已完成思考<span v-if="conversationData.robot.thinkingTime">（用时{{conversationData.robot.thinkingTime}}秒）</span></span>
                    </div>
                    <span v-if="conversationData.robot.content">
                      <img v-show="conversationData.robot.showDeepThinkContent" :src="AiCollapseImg" alt="icon"
                        class="ai-deepThink-collapase-icon-img">
                      <img v-show="conversationData.robot.showDeepThinkContent" :src="AiCollapseImgDark" alt="icon"
                        class="ai-deepThink-collapase-icon-img--dark">
                      <img v-show="!conversationData.robot.showDeepThinkContent" :src="AiExpandImg" alt="icon"
                        class="ai-deepThink-expand-icon-img">
                      <img v-show="!conversationData.robot.showDeepThinkContent" :src="AiExpandImgDark" alt="icon"
                        class="ai-deepThink-expand-icon-img--dark">
                    </span>
                  </div>
                  <div :class="conversationData.robot.showDeepThinkContent?(conversationData.robot.thinkingTime? 'deepThink-detail deepThink-detail-show':'deepThink-detail'):'deepThink-detail deepThink-detail-hidden'"
                    ref="deepThinkContentRef" @transitionend="transitionEnd_deepThinkContent">
                      <div :class="conversationData.robot.showDeepThinkContent?(conversationData.robot.thinkingTime? '':'deepThink-detail-show-thinking'):''">
                        <span class="depThink-detail-content" v-html="deepThinkContent"></span>
                      </div>
                      <div :class="conversationData.robot.showDeepThinkContent?(conversationData.robot.thinkingTime? '':'deepThink-detail-show-thinking-top'):''"></div>
                      <div :class="conversationData.robot.showDeepThinkContent?(conversationData.robot.thinkingTime? '':'deepThink-detail-show-thinking-bottom'):''"></div>
                  </div>
              </div>
            </div>
            <div class="markdown-content" v-if="mkHtml">
              <div ref="contentRef"
                :class="((conversationData.robot.referenceNumber && !conversationData.user.isDeepSearch) || (conversationData.user.isDeepSearch && mkHtml))? 'msg-pop-default needpadding' : 'msg-pop-default'">
                <span v-html="mkHtml" ref="popRef"></span>
                <!-- <span v-show="conversationData.robot.streaming" class="input-cursor" ref="cursorRef"></span> -->
                <span class="input-cursor" v-show="conversationData.robot.streaming" ref="cursorRef"><div class="input-cursor-loading"></div></span>
              </div>
            </div>
          </div>
        </template>
        <template
          v-if="conversationData.robot.errorMsg || (conversationData.robot.content === '' && conversationData.robot.needPause)">
          <div class="markdown-content-error">
            <div class="error-msg">{{ conversationData.robot.errorMsg }}</div>
            <div class="ai-tip" v-if="(conversationData.user.isDeepSearch && conversationData.robot.streamingDeepThinkText && !conversationData.robot.streaming && !conversationData.robot.errorMsg)">
              <div class="tip">以上内容为大模型生成，仅供参考</div>
              <div class="pauseTip" v-if="conversationData.robot.needPause">已停止生成</div>
            </div>
          </div>
        </template>

        <div
          v-if="(!conversationData.user.isDeepSearch && !conversationData.robot.streaming && conversationData.robot.content && !conversationData.robot.errorMsg) 
          || (conversationData.user.isDeepSearch  && conversationData.robot.content && !conversationData.robot.streaming && !conversationData.robot.errorMsg)">
          <div class="ai-tip">
            <div class="tip">以上内容为大模型生成，仅供参考</div>
            <div class="pauseTip" v-if="conversationData.robot.needPause">已停止生成</div>
          </div>
          <div class="normal-bottom-bar" v-if="!curContentQues && isLastItem">
            <div class="feedBackArea">
              <div @click="handleCopy">
                <img v-show="conversationData.robot.copyStatus" :src="AiCopiedImg" alt="icon"
                  class="ai-copied-icon-img" />
                <img v-show="conversationData.robot.copyStatus" :src="AiCopiedImg" alt="icon"
                  class="ai-copied-icon-img--dark" />

                <img v-show="!conversationData.robot.copyStatus"
                  :src="AiCopyImg" alt="icon"
                  class="ai-copy-icon-img" />
                <img v-show="!conversationData.robot.copyStatus"
                  :src="AiCopyImgDark" alt="icon"
                  class="ai-copy-icon-img--dark" />
              </div>
              <div @click="handleLike(true)">
                <img v-show="!conversationData.robot.likeStatus"
                  :src="AiLikeImg" alt="icon"
                  class="ai-like-icon-img" />
                <img v-show="!conversationData.robot.likeStatus"
                  :src="AiLikeImgDark" alt="icon"
                  class="ai-like-icon-img--dark" />

                <img v-show="conversationData.robot.likeStatus" :src="AiLikedImg" alt="icon"
                  class="ai-liked-icon-img--dark" />
                <img v-show="conversationData.robot.likeStatus" :src="AiLikedImg" alt="icon"
                  class="ai-liked-icon-img" />
              </div>
              <div @click="handleLike(false)">
                <img v-show="!conversationData.robot.unLikeStatus"
                  :src="AiUnLikeImg" alt="icon"
                  class="ai-unlike-icon-img" />
                <img v-show="!conversationData.robot.unLikeStatus"
                  :src="AiUnLikeImgDark" alt="icon"
                  class="ai-unlike-icon-img--dark" />

                <img v-show="conversationData.robot.unLikeStatus" :src="AiUnLikedImg" alt="icon"
                  class="ai-unliked-icon-img" />
                <img v-show="conversationData.robot.unLikeStatus" :src="AiUnLikedImgDark" alt="icon"
                  class="ai-unliked-icon-img--dark" />
              </div>
              <div class="lastDiv">
              </div>
            </div>
          </div>
          <!-- <div class="recommend" v-if="!curContentQues && isLastItem && conversationData.robot?.recommendQues?.length"> -->
          <div class="recommend" v-if="showRec">
            <div class="recommend-item" v-for="item in conversationData.robot.recommendQues" :key="item"
              @click="aiSearchByRec(item)">
              <span>{{ item }}</span>
              <!-- <img class="ai-recommend-item-img" :src="AiRecommendItemImg" alt="">
              <img class="ai-recommend-item-img--dark" :src="AiRecommendItemImgDark" alt=""> -->
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { computed, defineComponent, nextTick, ref, watch } from 'vue'

import AiLoadingSpinImg from '@/assets/img/ai-loading-spin.png'
import AiLoadingSpinImgDark from '@/assets/img/ai-loading-spin-dark.png'
import AiExpandImg from '@/assets/img/ai-expand.png'
import AiExpandImgDark from '@/assets/img/ai-expand-dark.png'
import AiCollapseImg from '@/assets/img/ai-collapse.png'
import AiCollapseImgDark from '@/assets/img/ai-collapse-dark.png'
import AiCopiedImg from '@/assets/img/ai-copied.svg'
import AiCopyImg from '@/assets/img/ai-copy.svg'
import AiCopyImgDark from '@/assets/img/ai-copy-dark.svg'
import AiLikeImg from '@/assets/img/ai-like.svg'
import AiLikeImgDark from '@/assets/img/ai-like-dark.svg'
import AiLikedImg from '@/assets/img/ai-liked.svg'
import AiUnLikedImgDark from '@/assets/img/ai-unLiked-dark.svg'
import AiUnLikeImg from '@/assets/img/ai-unLike.svg'
import AiUnLikeImgDark from '@/assets/img/ai-unLike-dark.svg'
import AiUnLikedImg from '@/assets/img/ai-unLiked.svg'
import defaultQuoteIcon from '@/assets/img/ai-default-quote-icon.jpg'
import AiWebSearchImg from '@/assets/img/ai-webSearch.svg'
import AiWebSearchImgDark from '@/assets/img/ai-webSearch-dark.svg'
import AiMoreImg from '@/assets/img/ai-more.png'
import AiMoreImgDark from '@/assets/img/ai-more-dark.png'
import AiRecommendItemImg from '@/assets/img/ai-recommend-item.png'
import AiRecommendItemImgDark from '@/assets/img/ai-recommend-item-dark.png'
import AiLoadingGif from '@/assets/lotties/ai-loading/ai-loading.json';
import AiDeepThinkImg from '@/assets/img/ai-deepThink.png'
import AiDeepThinkImg_label from '@/assets/img/ai-deepThink_label.svg'

import Lottie from "@/components/Lottie.vue"
import Skeleton from "@/components/Skeleton.vue"
import MarkdownIt from 'markdown-it'
import hljs from 'highlight.js'
import useClipboard from 'vue-clipboard3'
import 'highlight.js/styles/atom-one-dark-reasonable.css'
import { handleLikeApi } from '@/service/browserAiSearch'
import katex from "@vscode/markdown-it-katex"
import 'katex/dist/katex.min.css'
import { useCommonStore_aiSearch } from '@/stores/browserAiSearch'
import { storeToRefs } from 'pinia'
import { reportOnetrack_browser } from '@/utils/client'
import MarkdownItSup from 'markdown-it-sup'
// import { showToast } from 'vant';

export default defineComponent({
  components: { Lottie, Skeleton },
  props: {
    index: {
      type: Number,
      required: true,
    },
    conversationData: {
      type: Object,
      required: true
    },
    updateRefData: {
      type: Function,
      required: false
    },
    needMinHeight: {
      type: Boolean,
      required: false
    },
    isLastItem: {
      type: Boolean
    },
    curContentQues: {
      type: String,
    }
  },
  setup(props) {
    let inputHeights = '0px'
    const element = document.querySelector('.chat-container')
    if(element){
      let styles = window.getComputedStyle(element)
      inputHeights = styles.height
    }

    const update = (key: string, value: any) => {
      // 历史会话
      if (props.index !== -1) {
        let data = { ...props.conversationData.robot }
        data[key] = value
        const store_aiSearch = useCommonStore_aiSearch()
        let conversationList = store_aiSearch.conversationList
        conversationList[props.index].robot = data
        store_aiSearch.setConversationList(conversationList)
      }
      // 当前会话
      else {
        props.updateRefData && props.updateRefData(key, value)
      }
    }

    const showQuote = computed(() => {
      return props.conversationData.robot.showQuote || false
    })
    const quoteDetailRef = ref()
    // 引用文章的点击事件
    const handleClick_quote = () => {
      clickTrackFunc('reference','view_reference')
      if (showQuote.value) {
        let height = quoteDetailRef.value.offsetHeight;
        quoteDetailRef.value.style.height = height + "px";
        requestAnimationFrame(() => {
          quoteDetailRef.value.style.height = 0;
        });
      }
      else {
        quoteDetailRef.value.style.display = "block";
        quoteDetailRef.value.style.height = "auto";
        let height = quoteDetailRef.value.offsetHeight;
        quoteDetailRef.value.style.height = 0;
        requestAnimationFrame(() => {
          quoteDetailRef.value.style.height = height + "px";
        });
      }
      update('showQuote', !showQuote.value)
    }
    const transitionEnd = () => {
      if (showQuote.value) {
        quoteDetailRef.value.style.removeProperty("height");
      }
    }

    const streamingText = computed(() => {
      return props.conversationData.robot.content || ''
    })

    const showDeepThinkContent = computed(() => {
      return props.conversationData.robot.showDeepThinkContent || false
    })
    const deepThinkContentRef = ref()
    const handleClick_showdeepThink = () => {
      // console.log(streamingText.value)
      if(!streamingText.value){
        return
      }
      if (showDeepThinkContent.value) {
        let height = deepThinkContentRef.value.offsetHeight;
        deepThinkContentRef.value.style.height = height + "px";
        requestAnimationFrame(() => {
          deepThinkContentRef.value.style.height = 0;
        });
      }
      else {
        deepThinkContentRef.value.style.display = "block";
        deepThinkContentRef.value.style.height = "auto";
        let height = deepThinkContentRef.value.offsetHeight;
        deepThinkContentRef.value.style.height = 0;
        requestAnimationFrame(() => {
          deepThinkContentRef.value.style.height = height + "px";
        });
      }
      update('showDeepThinkContent', !showDeepThinkContent.value)
    }
    const transitionEnd_deepThinkContent = () => {
      if (showDeepThinkContent.value) {
        deepThinkContentRef.value.style.removeProperty("height");
      }
    }

    const aiSearchByRec = (query: string) => {
      // reportOnetrack_browser('ai_search_realatedquery_click',{'common_key':{},'query_content':query})
      window.aiSearch({
        query,
        searchSource:'AI_answer_page_reference',
        byRec: 'true',
        recIndex: props.index,
        LLM: 'DOUBAO',
      })
      clickTrackFunc('relate_query', query)
    }

    const aiDeepSearch = (query: string) => {
      window.aiSearch({ 
        query,
        searchSource:'AI_answer_page_deep_search',
        isDeep: true,
        LLM: 'DOUBAO',
      })
    }

    // markdown转html,并且高亮代码块
    const md = MarkdownIt({
      highlight: function (str: string, lang: string) {
        if (lang && hljs.getLanguage(lang)) {
          try {
            return `<div class="hl-code"><div class="hl-code-header"><span>${lang}</span></div><div class="hljs"><code>${hljs.highlight(str, { language: lang, ignoreIllegals: true }).value
              }</code></div></div>`
            // return `<div class="hl-code"><div class="hl-code-header"><span>${lang}</span><span class="copyBtn">copy</span></div><div class="hljs"><code>${hljs.highlight(str, { language: lang, ignoreIllegals: true }).value
            //   }</code></div></div>`
          } catch (e) {
            // console.log(e, 'error')
          }
        }
        return `<div class="hl-code"><div class="hl-code-header"><span>${lang}</span></div><div class="hljs"><code>${md.utils.escapeHtml(
          str
        )}</code></div></div>`
      }
    }).use(katex, { throwOnError: false, "errorColor" : "unset" }).use(MarkdownItSup)

    // 保存默认的表格渲染函数
    const defaultTableOpen = md.renderer.rules.table_open || function(tokens:any, idx:any, options:any, env:any, self:any) {
      return self.renderToken(tokens, idx, options);
    }

    const defaultTableClose = md.renderer.rules.table_close || function(tokens:any, idx:any, options:any, env:any, self:any) {
      return self.renderToken(tokens, idx, options);
    }

    // 覆盖规则：只在 <table> 外套 div
    md.renderer.rules.table_open = function(tokens:any, idx:any, options:any, env:any, self:any) {
      // 在 <table> 前添加 <div class="table-wrapper">
      return '<div class="markdown-table-wrapper">\n' + defaultTableOpen(tokens, idx, options, env, self);
    }

    md.renderer.rules.table_close = function(tokens:any, idx:any, options:any, env:any, self:any) {
      // 在 </table> 后闭合 </div>
      return defaultTableClose(tokens, idx, options, env, self) + '\n</div>';
    }

    // 覆盖默认的链接渲染规则
    md.renderer.rules.link_open = function(tokens:any, idx:any, options:any, env:any, self:any) {
      const token = tokens[idx];
      const hrefIndex = token.attrIndex('href');
      if (hrefIndex >= 0) {
        const href = token.attrs[hrefIndex][1];
        if (!href.startsWith('http://') && !href.startsWith('https://')) {
          // 或者完全移除跳转能力
          token.attrs.splice(hrefIndex, 1);
        }
      }
      return self.renderToken(tokens, idx, options);
    }

    // 保存原始的代码块渲染函数
    const defaultCodeBlockRender = md.renderer.rules.fence
    // 自定义代码块渲染
    md.renderer.rules.fence = function(tokens:any, idx:any, options:any, env:any, self:any) {
      const token = tokens[idx];
      // 检查代码内容是否为空或只有空白字符
      if (!token.content.trim()) {
        return '' // 返回空字符串，不渲染任何内容
      }
      // 否则使用默认渲染
      return defaultCodeBlockRender(tokens, idx, options, env, self)
    };

    /** 获取最后一个文本节点 */
    function getLastTextNode(node: Node | null): Node | null {
      if (!node) return null;
      if (node.nodeType === Node.TEXT_NODE && node.textContent?.trim()) {
        return node;
      }
      for (let i = node.childNodes.length - 1; i >= 0; i--) {
        const childNode = node.childNodes[i];
        const textNode = getLastTextNode(childNode);
        if (textNode) {
          return textNode
        }
      }
      return null;
    }
    const contentRef = ref() // 包含text和光标的容器节点
    const popRef = ref(); // text节点
    const cursorRef = ref(); // 光标节点
    /** 光标跟随逻辑 */
    function updateCursor() {
       //获取内容区宽度
      let contentWidth = 0 
      if (contentRef.value) {
        const width = contentRef.value.offsetWidth; // 获取宽度
        contentWidth = width
      }
      // 1. 找到最后一个文本节点
      let lastTextNode = getLastTextNode(popRef.value)
      // 2. 创建一个临时文本节点
      let tempText = document.createTextNode("\u200b"); // 零宽字符
      // 3. 将临时文本节点放在最后一个文本节点之后
      if (lastTextNode) {
        lastTextNode.parentNode && lastTextNode.parentNode.appendChild(tempText);
      } else {
        popRef.value && popRef.value.appendChild(tempText);
      }
      // 4. 获取临时文本节点距离父节点的距离（x,y）
      const range = document.createRange(); // 设置范围
      range.setStart(tempText, 0);
      range.setEnd(tempText, 0);
      const rect = range.getBoundingClientRect(); // 获取距离信息
      // 5. 获取当前文本容器距离视图的距离(x,y)
      const textRect = contentRef.value && contentRef.value.getBoundingClientRect();
      // 6. 获取到当前文本节点的位置，并将光标的位置插入到相应位置
      if (textRect) {
        const x = rect.left - textRect.left
        const y = rect.top - textRect.top
        // if (cursorRef.value) {
        //   cursorRef.value.style.transform = `translate(${x}px,${y}px)`;
        // }
        if (cursorRef.value) {
          if(x > (contentWidth - 20)){
            //光标到达边缘将光标移动到下一行
            cursorRef.value.style.transform = `translate(${x-(contentWidth-20)}px,${y+20}px)`;
          }else{
            cursorRef.value.style.transform = `translate(${x}px,${y}px)`;
          }
        }
      }
      
      // 7. 移除临时文本节点
      tempText.remove();
    }

    const streamingThinkText = computed(() => {
      return props.conversationData.robot.streamingDeepThinkText || ''
    })

    const deepThinkContent = computed(() => {
      return md.render(streamingThinkText.value)
    })

    const store = useCommonStore_aiSearch()
    const { webviewHeight, inputHeight, hideFeedbackPopFlag, appHeight, scrollItemHeight, maxScrollItemHeight } = storeToRefs(store)

    watch(hideFeedbackPopFlag, () => {
      showFeedBackFlag.value = false
    })

    const mHeight = computed(() => {
      return maxScrollItemHeight.value + 'px'
    })

    const streaming = computed(() => {
      return props.conversationData.robot.streaming || false
    })
    const mkHtml = computed(() => {
      let str = streamingText.value || ''
      // 替换 \( 和 \) 为 $
      str = str.replace(/\\\(/g, '$').replace(/\\\)/g, '$')
      // 替换 \[ 和 \] 为 $$
      str = str.replace(/\\\[/g, '$$').replace(/\\\]/g, '$$')
      str = str.replace(/\<sup\>/g, '^').replace(/\<\/sup\>/g, '^')
      let html = md.render(str)
      nextTick(() => {
        if (streaming.value) {
          updateCursor()
        }
        // else {
        //   // 传输结束后显示copy按钮并添加点击事件
        //   var elements = document.getElementsByClassName("copyBtn");
        //   for (var i = 0; i < elements.length; i++) {
        //     let element = elements[i] as HTMLElement;
        //     element.style.display = 'unset'
        //     element.addEventListener('click', (e: any) => {
        //       try {
        //         toClipboard(e.target?.parentElement.parentElement.lastElementChild.innerText)
        //       } catch (e) {
        //         console.error(e)
        //       }
        //     })
        //   }
        // }
      })
      return html
    })

    const copyStatus = computed(() => {
      return props.conversationData.robot.copyStatus || false
    })
    // 复制文字
    const { toClipboard } = useClipboard()
    const handleCopy = async () => {
      if(copyStatus.value){
        return
      }
      // reportOnetrack_browser('ai_search_answer_click',{'common_key':{},'function':'copy'})
      clickTrackFunc('copy','')
      let text = popRef.value.innerText
      if (!text) return
      try {
        await toClipboard(text)
        // eslint-disable-next-line no-undef
        // showToast('复制成功');
        showToast({
          message: '复制成功',
          position: 'bottom',
        })
        update('copyStatus', true)
        setTimeout(() => {
          update('copyStatus', false)
        }, 2000)
      } catch (e) {
        console.error(e)
      }
    }

    const likeStatus = computed(() => {
      return props.conversationData.robot.likeStatus || false
    })
    const unLikeStatus = computed(() => {
      return props.conversationData.robot.unLikeStatus || false
    })

    let likeFlag = false
    // 点赞、取消点赞、点踩、取消点踩
    const handleLike = async (like: boolean) => {
      if(likeFlag){
        return
      }
      // 1: 点赞 2: 取消点赞 3: 点踩 4: 取消点踩
      let feedbackType;
      // 点赞、取消点赞
      if (like) {
        // reportOnetrack_browser('ai_search_answer_click',{'common_key':{},'function':'up'})
        if (likeStatus.value) {
          feedbackType = 2
          clickTrackFunc('cancel_like','')
        } else {
          feedbackType = 1
          clickTrackFunc('like','')
        }
      }
      // 点踩、取消点踩
      else {
        // reportOnetrack_browser('ai_search_answer_click',{'common_key':{},'function':'down'})
        if (unLikeStatus.value) {
          feedbackType = 4
          clickTrackFunc('cancel_dislike','')
        } else {
          feedbackType = 3
          clickTrackFunc('dislike','')
        }
      }
      const params = {
        query: props.conversationData.user.content,
        oaid: props.conversationData.user.oaid,
        searchId: props.conversationData.user.searchId,
        feedbackType,
        business: 'BROWSER',
      }
      likeFlag = true
      if(!props.conversationData.user.oaid){
        // 点赞、取消点赞
        if (like) {
          // 判断点踩状态，如果已经点踩，则取消点踩,同时将点赞状态取反
          if (unLikeStatus.value) {
            update('unLikeStatus', false)
          }
          update('likeStatus', !likeStatus.value)
        }
        else {
          // 判断点赞状态，如果已经点赞，则取消点赞,同时将点踩状态取反
          if (likeStatus.value) {
            update('likeStatus', false)
          }
          update('unLikeStatus', !unLikeStatus.value)
        }
        likeFlag = false
        return
      }
      handleLikeApi(params).then(() => {
        // 点赞、取消点赞
        if (like) {
          // 判断点踩状态，如果已经点踩，则取消点踩,同时将点赞状态取反
          if (unLikeStatus.value) {
            update('unLikeStatus', false)
          }
          update('likeStatus', !likeStatus.value)
        }
        else {
          // 判断点赞状态，如果已经点赞，则取消点赞,同时将点踩状态取反
          if (likeStatus.value) {
            update('likeStatus', false)
          }
          update('unLikeStatus', !unLikeStatus.value)
        }
        likeFlag = false
      }).catch(() => {
        // console.log('点赞失败')
        likeFlag = false
      })
    }

    const showFeedBackFlag = ref(false)
    const showFeedBack = () => {
      showFeedBackFlag.value = !showFeedBackFlag.value
    }
    const hideFeedbackPop = ()=>{
      showFeedBackFlag.value = false
    }

    // 滚动到最底部
    // const clientHeight = document.documentElement.clientHeight;
    const clientHeight = computed(() => {
      return appHeight.value
    })

    const scrollItemHeights = computed(()=>{
      return scrollItemHeight.value
    })
    const app = document.querySelector('.scrollItem')
    const scrollToBottom = () => {
      nextTick(() => {
        if (app) {
          // 数字尽量大，更能触底
          app.scrollTop = app.scrollHeight || 1000000000
        }
      })
    }
    watch(mkHtml, (val) => {
      if (val) {
        if (app) {
          if (app.scrollTop + 3 > app.scrollHeight - scrollItemHeights.value) {
            scrollToBottom()
          }
        }
      }
    })
    
    watch(deepThinkContent, (val)=>{
      if(val){
        let deepThinkScrollDom = document.querySelectorAll('.deepThink-detail-show-thinking') as NodeListOf<HTMLElement>
        if(deepThinkScrollDom){
          if(deepThinkScrollDom.length){
            nextTick(()=>{
              deepThinkScrollDom[deepThinkScrollDom.length-1].scrollTop = 1000000000
            })
          }
        }
      }
    })
    watch(streaming, (v)=>{
      if(v.value){
        if (app) {
          if (app.scrollTop + 3 > app.scrollHeight - scrollItemHeights.value) {
            scrollToBottom()
          }
        }
      }
    })

    const recommendQues = computed(() => {
      return props.conversationData.robot.recommendQues?.length || 0
    })
    // watch(recommendQues, (v)=>{
    //   if(v){
    //     if(props.isLastItem && !props.curContentQues){
    //       if (app) {
    //         if (app.scrollTop + 3 > app.scrollHeight - scrollItemHeights.value) {
    //           scrollToBottom()
    //         }
    //       }
    //     }
    //   }
    // },{
    //   deep:true,
    //   immediate:true,
    // })

    let store_aiSearch = useCommonStore_aiSearch()
    let sessionId = store_aiSearch.sessionId
    let source = store_aiSearch.source
    let { hasChooseDeep } = storeToRefs(store_aiSearch)
    const clickTrackFunc = (clickType:string, clickElement:string)=>{
      if(!props.conversationData.user.searchId){
        return
      }
      let clickTrackParams = {
        'common_key': {},
        'page_style':'H5',
        'aisearch_query': props.conversationData.user.content || '',
        'ai_request_id': props.conversationData.user.searchId,
        'ai_session_id': sessionId,
        'LLM':hasChooseDeep.value?'deepseek':'DOUBAO',
        'deep_think': hasChooseDeep.value,
        'click_type': clickType,
        'click_element': clickElement,
        'search_api': props.conversationData.user.isWebSearch,
      }
      reportOnetrack_browser('ai_search_answer_click',clickTrackParams)
    }

    // 跳转引用文章的链接
    const handleGoWebSite = (url: string) => {
      setTimeout(() => {
        window.open(url, '_blank')
        clickTrackFunc('reference', url)
      }, 300);
    }

    const currentChoosenStatus = computed(()=>{
      let type = '2'
      if( props.conversationData.user.isDeepSearch && !props.conversationData.user.isWebSearch){
        type =  '1'
      }
      else if( !props.conversationData.user.isDeepSearch && props.conversationData.user.isWebSearch){
        type = '2'
      }
      else if( props.conversationData.user.isDeepSearch && props.conversationData.user.isWebSearch){
        type = '3'
      }
      else if( !props.conversationData.user.isDeepSearch && !props.conversationData.user.isWebSearch){
        type = '4'
      }
      return type
    })

    const thinkingTime = computed(()=>{
      return props.conversationData.robot.thinkingTime || 0
    })

    watch(thinkingTime, (newV)=>{
      if(newV){
        update('showDeepThinkContent', false)
      }
    })

    const referenceNumber_computed = computed(()=>{
      return props.conversationData.robot.referenceNumber || 0
    })

    let referenceNumber_used = ref(0)
    let referenceNumber_all = ref(0)
    watch(referenceNumber_computed, (newV)=>{
      if(newV){
        if(props.index === -1){
          referenceNumber_all.value = newV + Math.floor(Math.random() * (20 - 8 + 1) + 8)
          setTimeout(() => {
            if(props.conversationData.robot.needPause){
              return
            }
            referenceNumber_used.value = newV
          }, 500);
        }
        else {
          referenceNumber_used.value = newV
        }
      }
    },{
      immediate:true,
      deep:true,
    })

    const showImgs = computed(()=>{
      let data =  JSON.parse(props.conversationData.robot.referenceData).slice(0,3)
      let imgs:string[] = []
      data.forEach((item:any)=>{
        if(item.icon){
          imgs.push(item.icon)
        }
        else {
          imgs.push('')
        }
      })
      return imgs
    })

    const handlErrorImg = (e: any) => {
      e.target.src = defaultQuoteIcon
    }


    const a = computed(()=>{
      return (!props.conversationData.user.isDeepSearch && !props.conversationData.robot.streaming && props.conversationData.robot.content && !props.conversationData.robot.errorMsg) 
      || (props.conversationData.user.isDeepSearch  && props.conversationData.robot.content && !props.conversationData.robot.streaming && !props.conversationData.robot.errorMsg)
    })

    const b = computed(()=>{
      return !props.curContentQues && props.isLastItem && props.conversationData.robot?.recommendQues?.length
    })

    const c = computed(()=>{
      return (props.conversationData.robot?.showRec ==='true')
    })

    const showRec = ref(false)

    if(a.value && b.value && !props.conversationData.robot?.showRec){
      showRec.value = true
    }
    else {
      showRec.value = false
    }

    const scrollToBottomSmooth = () => {
      nextTick(()=>{
        if (app) {
          app.scrollTo({
            top: app.scrollHeight || 1000000000,
            behavior: 'smooth'
          })
        }
      })
    }

    const showR = async () => {
      let toBottom = false
      if (app) {
        if (app.scrollTop + 20 > app.scrollHeight - scrollItemHeights.value) {
          toBottom = true
        }
      }
      if(app){
        let scrollTopBefore = app.scrollTop
        showRec.value = true
        await nextTick(() => {})
        app.scrollTop = scrollTopBefore
      }
      if(toBottom){
        scrollToBottomSmooth()
      }
    }
    watch([a,b,c], ([newA, newB, newC])=>{
      if(newA && newB && newC){
        setTimeout(() => {
          showR()
        },200)
      }
      else {
        showRec.value = false
      }
    })
    return {
      AiLoadingSpinImg,
      AiLoadingSpinImgDark,
      AiExpandImg,
      AiExpandImgDark,
      AiCollapseImg,
      AiCollapseImgDark,
      AiCopiedImg,
      AiCopyImg,
      AiCopyImgDark,
      AiLikeImg,
      AiLikeImgDark,
      AiLikedImg,
      AiUnLikeImg,
      AiUnLikeImgDark,
      AiUnLikedImg,
      quoteDetailRef,
      handleClick_quote,
      transitionEnd,
      mkHtml,
      handleCopy,
      handleLike,
      popRef,
      contentRef,
      cursorRef,
      mHeight,
      AiLoadingGif,
      defaultQuoteIcon,
      AiWebSearchImg,
      AiWebSearchImgDark,
      AiMoreImgDark,
      AiMoreImg,
      AiRecommendItemImg,
      AiRecommendItemImgDark,
      AiUnLikedImgDark,
      aiSearchByRec,
      // iHeight,
      showFeedBack,
      showFeedBackFlag,
      aiDeepSearch,
      AiDeepThinkImg,
      AiDeepThinkImg_label,
      handleClick_showdeepThink,
      transitionEnd_deepThinkContent,
      deepThinkContentRef,
      // elementExposeTrackParams_deepseekBtn,
      inputHeight,
      deepThinkContent,
      sessionId,
      inputHeights,
      source,
      handleGoWebSite,
      currentChoosenStatus,
      referenceNumber_used,
      referenceNumber_all,
      showImgs,
      handlErrorImg,
      showRec,
    }
  }
})
</script>
<style lang="less" scoped>
@import './base-styles.less';
@keyframes skeleton-loading {
  0% {
    transform: translateX(-100%);
  }
  100% {
    transform: translateX(100%);
  }
}
// -------------------------- 深色模式适配 -------------------
@media (prefers-color-scheme: dark) {
  .answerBox {
    --ai-question-text-color: rgba(255, 255, 255, 0.95);
    --ai-loading-text-color: rgba(255, 255, 255, 0.6);
    --ai-loading-bg-color: rgba(191, 206, 255, 0.14);
    --ai-quote-bg-color: rgba(191, 206, 255, 0.14);
    --ai-quote-title-text-color: rgba(255, 255, 255, 0.6);
    --ai-quote-detail-text-color: rgba(255, 255, 255, 0.7);
    --ai-markdown-content-text-color: rgba(255, 255, 255, 0.7);
    --ai-tip-text-color: rgba(255, 255, 255, 0.3);
    --ai-pause-tip-text-color: rgba(255, 255, 255, 0.5);
    --ai-markdown-content-error-text-color: rgba(255, 255, 255, 0.9);
    --ai-noErrorMsg-needPause-text-color: rgba(255, 255, 255, 0.4);
    --ai-webSearch-bg-color: rgba(191, 206, 255, 0.14);
    --ai-webSearch-text-color: rgba(255, 255, 255, 0.7);
    --ai-recommend-item-bg-color: rgba(36, 36, 36, 0.8);
    --ai-recommend-item-text-color: rgba(255, 255, 255, 0.7);
    --ai-feefback-bg-color: #1c1d22;
    --ai-feedback-border-color: rgba(255, 255, 255, 0.1);
    --ai-feedback-shadow-color: rgba(255, 255, 255, 0.03);
    --ai-recommend-line-color: rgba(255, 255, 255, 0.1);
    --ai-deepSearch-bg-color: rgba(52, 130, 255, 0.14);
    --ai-deepThink-tip-bg-color: rgba(79, 107, 254, 0.1);
    --ai-deepThink-content-text-color: rgba(255, 255, 255, 0.6);
    --ai-deepThink-detail-text-color: rgba(255, 255, 255, 0.5);
    --ai-cursor-color: rgba(255, 255, 255, 0.7);
    --ai-skeleton-animation-color1: rgba(0, 0, 0, 0.1);
    --ai-skeleton-animation-color2: rgba(0, 0, 0, 0.5);
    --ai-skeleton-animation-color3: rgba(191, 206, 255, 0);
    --ai-answer-top-border-color: rgba(255,255,255,0.3);
    --ai-deepThink-color1: rgba(0, 0, 0, 0.8);
    --ai-deepThink-color2: rgba(0, 0, 0, 0);
    --ai-deepThink-color3: rgba(0, 0, 0, 0);
    --ai-deepThink-color4: rgba(0, 0, 0, 0.8);
    --ai-recQues-ques-border-color: rgba(255, 255, 255, 0.4);
  }
  .questions {
    --ai-questions-bg-color: rgba(52, 130, 255, 0.4);
  }

  .ai-expand-icon-img,
  .ai-skeleton-ion-img,
  .ai-collapase-icon-img {
    display: none;

    &--dark {
      display: inline;
    }
  }

  .ai-copy-icon-img,
  .ai-like-icon-img,
  .ai-loading-icon-img,
  .ai-more-icon-img,
  .web-search-img,
  .ai-deepThink-collapase-icon-img,
  .ai-deepThink-expand-icon-img,
  .ai-recommend-item-img,
  .ai-unlike-icon-img,
  .ai-unliked-icon-img,
  .ai-liked-icon-img,
  .ai-copied-icon-img {
    display: none;

    &--dark {
      display: block;
    }
  }
}

// -------------------------- 浅色模式适配 -------------------
@media (prefers-color-scheme: light) {
  .answerBox {
    --ai-question-text-color: rgba(36, 41, 51, 1);
    --ai-loading-text-color: rgba(51, 68, 102, 0.8);
    --ai-loading-bg-color: rgb(245 247 251);
    --ai-quote-bg-color: rgb(247 249 251);
    --ai-quote-title-text-color: rgba(51, 68, 102, 0.8);
    --ai-quote-detail-text-color: #334466;
    --ai-markdown-content-text-color: #242933;
    --ai-tip-text-color: rgba(36, 41, 51, 0.3);
    --ai-pause-tip-text-color: rgba(0, 0, 0, 0.4);
    --ai-markdown-content-error-text-color: rgba(0, 0, 0, 0.9);
    --ai-noErrorMsg-needPause-text-color: rgba(0, 0, 0, 0.4);
    --ai-webSearch-bg-color:rgba(0, 43, 128, 0.03);
    --ai-webSearch-text-color: rgba(51, 68, 102, 1);
    --ai-recommend-item-bg-color: rgba(0, 43, 128, 0.03);
    --ai-recommend-item-text-color: rgba(51, 68, 102, 0.9);
    --ai-feefback-bg-color: rgba(255, 255, 255, 1);
    --ai-feedback-border-color: rgba(0, 0, 0, 0.1);
    --ai-feedback-shadow-color: rgba(0, 0, 0, 0.03);
    --ai-recommend-line-color: rgba(0, 0, 0, 0.05);
    --ai-deepSearch-bg-color: rgba(52, 130, 255, 0.1);
    --ai-deepThink-tip-bg-color: rgba(79, 107, 254, 0.1);
    --ai-deepThink-content-text-color: rgba(51, 68, 102, 0.8);
    --ai-deepThink-detail-text-color: rgba(51, 68, 102, 0.8);
    --ai-cursor-color: #242933;
    --ai-skeleton-animation-color1: rgba(255, 255, 255, 0.1);
    --ai-skeleton-animation-color2: rgba(255, 255, 255, 0.5);
    --ai-skeleton-animation-color3: rgba(10, 43, 128, 0);
    --ai-answer-top-border-color: rgba(0,0,0,0.1);
    --ai-deepThink-color1: rgba(250, 251, 252, 0.8);
    --ai-deepThink-color2: rgba(250, 251, 252, 0);
    --ai-deepThink-color3: rgba(250, 251, 252, 0);
    --ai-deepThink-color4: rgba(250, 251, 252, 0.8);
    --ai-recQues-ques-border-color: #cfd0d0;
  }
  .questions {
    --ai-questions-bg-color: rgba(52, 130, 255, 0.1);
  }

  .ai-expand-icon-img,
  .ai-skeleton-ion-img,
  .ai-collapase-icon-img {
    display: inline;

    &--dark {
      display: none;
    }
  }

  .ai-copy-icon-img,
  .ai-like-icon-img,
  .ai-loading-icon-img,
  .ai-more-icon-img,
  .web-search-img,
  .ai-deepThink-collapase-icon-img,
  .ai-deepThink-expand-icon-img,
  .ai-recommend-item-img,
  .ai-unlike-icon-img,
  .ai-unliked-icon-img,
  .ai-liked-icon-img,
  .ai-copied-icon-img {
    display: block;

    &--dark {
      display: none;
    }
  }
}

.more-icon-container {
  position: relative;
  .feedback-mask {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    z-index: 998;
  }
  .feedback-container {
    background-color: var(--ai-feefback-bg-color);
    border: 0.5px solid var(--ai-feedback-border-color);
    width: 174px;
    height: 50px;
    line-height: 50px;
    border-radius: 16px;
    font-size: 16px;
    font-weight: 500;
    font-family: MiSans;
    padding-left: 20px;
    position: absolute;
    top: 46px;
    right: -6px;
    box-shadow: 0px 0.95px 3.96px 0px var(--ai-feedback-shadow-color);
    box-shadow: 0px 7.04px 15.84px 0px var(--ai-feedback-border-color);
    z-index: 999;
  }

}

.msgContainer {
  box-sizing: border-box;
  padding-bottom: 40px;
}
// .msgContainer:nth-of-type(2){
//   margin-top: 0;
// }
.needPaddingBottom {
  // padding-bottom: 144px;
}

.questions-box {
  display: flex;
  justify-content: flex-end;
  user-select: text !important;
}
.questions {
  font-size: 16px;
  color: var(--ai-question-text-color);
  font-weight: 500;
  font-family: 'MiSans';
  line-height: 22px;
  position: relative;
  margin: 15px 0 34px 10px;
  padding: 13px 18px;
  word-wrap: break-word;
  background-color: var(--ai-questions-bg-color);
  border-radius: 10px;
  overflow: hidden;
  user-select: text !important;
  white-space: pre-line;
}

.answerBoxContainer {
  border-radius: 20px;
  overflow: hidden;
  padding: 18px;
  box-sizing: border-box;
}

.answerBox {
  width: 100%;

  .loadingBox {

    .loadingTip {
      display: flex;
      justify-content: flex-start;
      align-items: center;
      padding-left: 14px;
      height: 47px;
      line-height: 47px;
      border-radius: 10px;
      // background-color: var(--ai-loading-bg-color);
      margin-bottom: 30px;
      border: 0.7px solid var(--ai-answer-top-border-color);
      position: relative;
      .ai-loading-icon {
        width: 20px;
        height: 20px;
        margin-right: 4px;
      }

      .text-loading {
        color: var(--ai-loading-text-color);
        font-family: MiSans;
        font-size: 15.3px;
        font-weight: 400;
        position: relative;
        // margin-left: 6px;
      }
      .text-loading::after {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 100px;
        height: 100%;
        animation: skeleton-loading 1.5s ease 0s infinite;
        background: linear-gradient(
          to left,
          var(--ai-skeleton-animation-color1) 0,
          var(--ai-skeleton-animation-color2) 80%,
          var(--ai-skeleton-animation-color3) 100%
        );
        transform: skewX(-45deg);
      }
    }

    .aiSkeleton {
      width: 100%;
      height: 278px;
      margin-top: 24px;

      img {
        width: 100%;
        height: 100%;
      }
    }

    .pause_step {
      font-size: 14px;
      color: var(--ai-noErrorMsg-needPause-text-color);
      font-family: 'MiSans';
      font-weight: 330;
      line-height: 24px;
    }
  }

  .answers {
    word-break: break-all;
    .answer-top {
      border: 1px solid var(--ai-answer-top-border-color);
      border-radius: 12px;
    }
    .quoteIcon-title {
      width: 30px;
      height: 30px;
      border-radius: 50%;
      overflow: hidden;
      margin-right: -5px;
      vertical-align: middle;
      margin-top: -4px !important;
    }
    .quote {
      // background-color: var(--ai-quote-bg-color);
      border-radius: 12px;
      padding: 0 12px 0 12px;
      margin-top: 2px;
      .quote-title {
        .quote-title-sourceNumber {
          margin-left: 10px;
        }
        height: 46px;
        font-family: MiSans;
        font-size: 15.3px;
        font-weight: 400;
        display: flex;
        align-items: center;
        justify-content: space-between;
        color: var(--ai-quote-title-text-color);

        img {
          width: 20px;
          height: 20px;
          margin-top: 2px;
        }
        img:last-of-type {
          margin-right: 0;
        }
      }

      .quote-detail {
        overflow: hidden;
        overflow-y: scroll;
        transition: all .3s;
        // display: none;
        display: block;
        max-height: 360px;

        div {
          font-family: 'MiSans';
          color: var(--ai-quote-detail-text-color);
          font-size: 14px;
          font-weight: 400;
          margin-bottom: 14px;
          box-sizing: border-box;
          word-wrap: break-word;
          overflow: hidden;
          white-space: nowrap;
          text-overflow: ellipsis;
          line-height: 22px;
        }

        .quoteIcon {
          width: 20px;
          height: 20px;
          border-radius: 50%;
          overflow: hidden;
          margin-right: 8px;
          vertical-align: middle;
          margin-top: -2px;
        }

      }
      .quote-detail-show {
        display: block;
      }
      .quote-detail-hidden {
        height: 0;
      }
    }
    .needMargin {
      margin-top: 14px;
    }
    .deepThinkContentBox {
      // background: var(--ai-quote-bg-color);
      border-radius: 12px;
      padding: 0px 12px 8px 12px;
      
      font-size: 15.3px;
      line-height: 24px;
      font-family: Misans;
      font-weight: 350;
      .thinkTitle {
        display: flex;
        position: relative;
        color: var(--ai-deepThink-content-text-color);
        font-weight: 400;
        margin-bottom: 4px;
        font-size: 15.3px;
        img {
          width: 20px;
          height: 20px;
          margin-top: 2px;
          position: absolute;
          right: 0;
        }
      }
      .depThink-detail-content {
        font-size: 14.3px;
        user-select: text !important;
      }
      .deepThink-detail {
        position: relative;
        overflow: hidden;
        transition: all .3s;
        // display: none;
        color: var(--ai-deepThink-detail-text-color);
        .deepThink_tip {
          width: 110px;
          height: 24px;
          border-radius: 6px;
          display: flex;
          justify-content: center;
          align-items: center;
          font-size: 12px;
          font-weight: 330;
          background: var(--ai-deepThink-tip-bg-color);
          color: rgba(79, 107, 254, 1);
          margin: 8px 0 12px 0;
          img {
            width: 11px;
            height: 11px;
            margin-right: 4px;
          }
        }
        :deep(.depThink-detail-content>p) {  
          margin-bottom: 12.4px !important;
        }
        :deep(.depThink-detail-content>p:last-child) {  
          margin-bottom: 0 !important;
        }
        :deep(.depThink-detail-content h1),
        :deep(.depThink-detail-content h2),
        :deep(.depThink-detail-content h3),
        :deep(.depThink-detail-content h4),
        :deep(.depThink-detail-content h5),
        :deep(.depThink-detail-content h6) {
          font-size: 15.3px !important;
        }
      }
      .deepThink-detail-show {
        // display: block;
        margin-bottom: 6px;
        
      }
      .deepThink-detail-hidden {
        height: 0;
      }
      .deepThink-detail-show-thinking {
        display: block;
        max-height: 144px;
        overflow-y: scroll;
      }
      .deepThink-detail-show-thinking-top {
        content: "";
        position: absolute;
        top: 0px;
        left: 0;
        width: 100%;
        height: 30px;
        // background: linear-gradient(rgba(255, 255, 255, 0.8) 0%, rgba(255, 255, 255, 0) 100%);
        // background: linear-gradient(rgba(0, 0, 0, .8) 0%, rgba(0, 0, 0, 0) 100%);
        background: linear-gradient(var(--ai-deepThink-color1) 0%, var(--ai-deepThink-color2) 100%);
      }
      .deepThink-detail-show-thinking-bottom {
        content: "";
        position: absolute;
        bottom: 0px;
        left: 0;
        width: 100%;
        height: 30px;
        // background: linear-gradient(rgba(255, 255, 255, 0) 0%, rgba(255, 255, 255, 0.8) 100%);
        // background: linear-gradient(rgba(0, 0, 0, 0) 0%, rgba(0, 0, 0, 0.8) 100%);
        background: linear-gradient(var(--ai-deepThink-color3) 0%, var(--ai-deepThink-color4) 100%);
      }
    }
    .needp {
      padding-top: 12px;
    }

    .markdown-content {
      font-size: 16.4px;
      font-family: 'MiSans';
      color: var(--ai-markdown-content-text-color);
      line-height: 26.2px;
      font-weight: 400;
      user-select: text !important;

      .msg-pop-default {
        position: relative;
      }

      .needpadding {
        padding-top: 20px;
      }

    }

    .markdown-content-error {
      .error-msg {
        font-size: 15px;
        font-family: 'MiSans';
        color: var(--ai-markdown-content-error-text-color);
        line-height: 24px;
        font-weight: 330;
      }

      .error-bottom-bar {
        margin-top: 28px;
        margin-bottom: 60px;
        display: flex;
        justify-content: space-between;
        font-family: MiSans;

        .web-search {
          background-color: var(--ai-webSearch-bg-color);
          border-radius: 10px;
          // border: 0.5px solid rgba(52, 130, 255, 0.2);
          height: 42px;
          display: flex;
          align-items: center;
          padding: 0 14px 0 8px;

          .web-search-icon {
            width: 24px;
            height: 24px;
            // display: unset;
            margin-right: 4px;
          }

          span {
            color: var(--ai-webSearch-text-color);
            font-size: 14px;
            font-weight: 400;
          }

        }

        .ai-more-icon-img--dark,
        .ai-more-icon-img {
          width: 42px;
          height: 42px;
        }
      }
    }
  }

  .ai-tip {
    .tip {
      font-size: 10px;
      font-family: 'MiSans';
      font-weight: 400;
      margin-top: 14px;
      color: var(--ai-tip-text-color);
      line-height: 13px;
    }

    .pauseTip {
      margin-top: 14px;
      font-size: 15px;
      font-family: 'MiSans';
      font-weight: 400;
      color: var(--ai-pause-tip-text-color);
      line-height: 24px;
    }
  }

  .deepSearchContainer {
    width: 100%;
    height: 42px;
    display: flex;
    justify-content: center;
    align-items: center;
    border-radius: 10px;
    border: 0.5px solid rgba(52, 130, 255, 0.2);
    background: var(--ai-deepSearch-bg-color);
    color: rgba(52, 130, 255, 1);
    font-family: MiSans;
    font-weight: 400;
    font-size: 14px;
    margin-top: 18px;
    img {
      width: 15px;
      height: 15px;
      margin-right: 8px;
    }

  }

  .normal-bottom-bar {
    // margin: 28px 0 32px 0;
    margin: 22.8px 0 22.8px 0;
    // padding-bottom: 28px;
    display: flex;
    justify-content: flex-start;
    align-items: center;
    font-family: MiSans;

    .web-search {
      background-color: var(--ai-webSearch-bg-color);
      border-radius: 10px;
      height: 42px;
      display: flex;
      align-items: center;
      padding: 0 14px 0 8px;

      img {
        width: 24px;
        height: 24px;
        // display: block;
        margin-right: 4px;
      }

      span {
        color: var(--ai-webSearch-text-color);
        font-size: 14px;
        font-weight: 400;
      }

    }

    .feedBackArea {
      display: flex;
      justify-content: center;
      align-items: center;

      img {
        width: 24px;
        height: 24px;
        margin-right: 18px;
      }

      .lastDiv {
        img {
          margin-right: 0
        }
      }

      .ai-unliked-img {
        display: block;
      }

    }
  }

  .recommend {
    margin-bottom: 6px;
    // padding-top: 20px;
    // border-top: 1px solid var(--ai-recommend-line-color);
    .recommend-item {
      width: fit-content;
      max-width: calc(100% - 24px);
      height: 40px;
      border-radius: 10px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-size: 15px;
      color: var(--ai-recommend-item-text-color);
      border: 0.7px solid var(--ai-recQues-ques-border-color);
      // backdrop-filter: blur(200px);
      padding: 0 12px;
      margin-bottom: 9px;
      span {
        overflow: hidden;
        text-overflow: ellipsis;
        word-wrap: break-word;
        white-space: nowrap;
      }

      img {
        width: 20px;
        height: 20px;
      }
    }

    .recommend-item:last-child {
      margin-bottom: 0;
    }
  }
}
</style>
<style scoped lang="less">
.msg-pop-default {
  :deep(ol ul) {
    list-style-type: circle;
    margin-block-start: 0px;
    margin-block-end: 0px;
  }
  :deep(ul) {
    display: block;
    list-style-type: disc;
    margin-block-start: 1em;
    margin-block-end: 1em;
    margin-inline-start: 0px;
    margin-inline-end: 0px;
    // padding-inline-start: 40px;
  }
  :deep(ol){
    display: block;
    list-style-type: decimal;
    margin-block-start: 1em;
    margin-block-end: 1em;
    margin-inline-start: 0px;
    margin-inline-end: 0px;
    // padding-inline-start: 40px;
  }
  :deep(ol ul ul) {
    list-style-type: square;
  }
  :deep(ul ul) {
    list-style-type: circle;
  }
  :deep(.katex-display) {
    margin: 0;
  }

  :deep(.katex) {
    // overflow-x: auto;
    // overflow-y: hidden;
    // display: block;
    // text-align: center;
  }

  :deep(ol) {
    margin-top: 0;
    margin-bottom: 0;

    :deep(ul) {
      padding-left: 0;
    }
  }

  :deep(li) {
    list-style: inherit !important;

    ul {
      padding-left: 8px !important;
    }
  }

  :deep(ul>li>ul) {
    padding-left: 16px !important;
  }

  :deep(p) {
    margin-bottom: 0;
    white-space: pre-line;
    word-break: break-all;
  }
  :deep(table) {
    white-space: pre-line;
    word-break: break-all;
  }

  :deep(h1),
  :deep(h2),
  :deep(h3),
  :deep(h4),
  :deep(h5),
  :deep(h6) {
    line-height: 1.3;
    font-size: 17.5px;
    margin: 0;
    padding: 0;
  }

  :deep(>span>h1),
  :deep(>span>h2),
  :deep(>span>h3),
  :deep(>span>h4),
  :deep(>span>h5),
  :deep(>span>h6) {
    margin-bottom: 13.8px;
    margin-top: 27.6px;
  }

  :deep(strong) {
    font-weight: bold;
  }
  :deep(>span>p) {
    margin-bottom: 24px;
    overflow-x: scroll;
  }

  :deep(>span>p:last-child) {
    margin-bottom: 0px;
    margin-top: 27.6px;
  }

  :deep(>span>ol) {
    margin-bottom: 10px;
    padding-left: 20px;
  }

  :deep(>span>ol>li) {
    margin-bottom: 13.8px;
  }

  :deep(>span>ol>li:last-child) {
    margin-bottom: 0;
  }

  :deep(>span>ol>li>p:has(strong)) {
    margin-bottom: 10px;
  }

  :deep(>span>ol>li>p>strong) {
    margin-bottom: 10px;
  }

  :deep(>span>ol>li>ul>li) {
    margin-bottom: 6px;
  }

  
  :deep(>span>ul>li>ul>li) {
    margin-bottom: 6px;
  }

  :deep(>span>ul) {
    padding-left: 20px;
    margin-top: 12.4px;
    margin-bottom: 12.4px;
    overflow-x: scroll;
    overflow-y: hidden;
  }
  :deep(>span>ul>li) {
    margin-bottom: 6px;
  }
  :deep(>span>ul>li>ul) {
    margin-bottom: 12.4px;
    margin-top: 6px;
  }
  :deep(>span>ul>li:last-child) {
    margin-bottom: 0;
  }
  :deep(br) {
    display: none;
  }
  :deep(hr){
    height: 0.6px;
    background: rgba(0, 0, 0, 0.15);
    border: none;
    display: block;
  }
  :deep(>span>:first-child){
    margin-top: 0 !important;
  }

  // 表格样式
  :deep(table){
    border-collapse: collapse;
  }
  :deep(th:first-child ){
    padding-left: 0;
  }
  :deep(td:first-child ){
    padding-left: 0;
  }
  :deep(td){
    border-bottom: 1px solid rgba(163, 163, 163, 0.6);
    padding: 6px 12px;
  }
  :deep(th){
    text-align: left;
    border-bottom: 1px solid rgba(163, 163, 163,0.8);
    border-top: 1px solid rgb(163, 163, 163);
    padding: 6px 12px;
    font-weight: 600;
    border-top: none;
  }

  // 图片样式
  :deep(img){
    max-width: 100%;
  }
  :deep(.katex-display) {
    overflow-x: auto;
    overflow-y: hidden;
  }
  :deep(.markdown-table-wrapper) {
    overflow-x: auto;
  }
  :deep(.markdown-table-wrapper table) {
    border-collapse: collapse;
    width: max-content;
    max-width: max-content;
  }
  :deep(.markdown-table-wrapper td) {
    min-width: 82px;
    max-width: 220px;
  }
}
</style>
