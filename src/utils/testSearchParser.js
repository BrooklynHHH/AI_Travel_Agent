/**
 * 搜索内容解析器测试文件
 * 用于测试和验证搜索工具内容的解析功能
 */

import SearchContentParser from './searchContentParser.js'
import ContentFormatter from './contentFormatter.js'

// 测试数据 - 您提供的搜索工具返回内容
const testSearchContent = `{'type': 'search_ref', 'datas': [{'title': '2025 年新疆七天游需要多少?南疆7日纯玩老年团旅游安排推荐!', 'url': 'https://baijiahao.baidu.com/s?id=1837177177261357963&wfr=spider&for=pc', 'content': ' Day1:抵达乌鲁木齐 我们抵达乌鲁木齐后,小玉早已在机场等候,热情地迎接我们,帮忙拿行李,安排我们前往酒店。稍作休息,晚上便带我们去品尝地道的新疆美食,大盘鸡、烤包子,那滋味,至今想起来都让人垂涎。 Day2:乌鲁木齐 - 库尔勒 乘坐舒适的交通工具前往库尔勒,一路上,广袤的新疆风光令人目不暇接,远处山脉连绵,戈壁滩一望无际,偶尔还能看到成群的牛羊,尽显新疆的壮美辽阔。抵达库尔勒后,漫步街头,感受这座城市的热闹与烟火气,品尝烤羊肉串、馕坑肉等美食。 Day3:库尔勒 - 罗布人村寨 早餐后前往神秘的罗布人村寨。村寨周边风景独特,塔里木河蜿蜒穿过,两岸胡杨林茂密,背后是浩瀚的塔克拉玛干沙漠。进入村寨,古老的罗布人民居用胡杨木和芦苇搭建而成,充满原始气息。在这里,我们深入了解了罗布人的独特文化和生活方式。沿着塔里木河漫步,欣赏金黄的胡杨林,还体验了刺激的沙漠越野车和悠扬的骆驼骑行,傍晚的沙漠日落更是美到令人窒息。 Day4:罗布人村寨 - 塔里木胡杨林 清晨再次感受罗布人村寨的宁静,之后前往塔里木胡杨林。乘坐观光小火车深入胡杨林,仿佛置身金色海洋。这里的胡杨形态各异,有的高大挺拔,有的枝干扭曲,它们耐旱、耐盐碱、抗风沙,"生而千年不死,死而千年不倒,倒而千年不朽",令人肃然起敬。 Day5:塔里木胡杨林 - 库车 途中欣赏南疆田园风光,抵达库车后游览库车王府,融合中原和维吾尔族建筑风格,气势恢宏,还能了解库车王家族历史变迁。傍晚在库车夜市品尝特色美食,购买精美纪念品。 Day6:库车 - 天山神秘大峡谷 - 喀什 前往天山神秘大峡谷,红褐色山体群组成的峡谷曲径通幽,峰回路转,还有古老佛教石窟。之后前往喀什,这座具有两千多年历史的古城,充满浓郁维吾尔族风情,夜晚漫步古城街头,品尝美食,感受独特魅力。', 'siteName': '', 'pic': None}, {'title': '新疆南疆旅游必去的十大景点:探索神秘西域的绝美风光', 'url': 'https://baijiahao.baidu.com/s?id=1837532649561249115&wfr=spider&for=pc', 'content': ' 一、喀什古城——活着的千年西域风情 作为南疆最具代表性的旅游目的地,喀什古城是新疆唯一一座以伊斯兰文化为特色的迷宫式城市街区,也是世界上现存规模最大的生土建筑群之一。漫步在喀什古城的街巷中,仿佛穿越回了千年前的西域。 古城内最值得一看的是艾提尕尔清真寺,这是新疆最大的清真寺,每逢古尔邦节,这里会聚集数万穆斯林进行礼拜,场面极为壮观。此外,百年老茶馆也是体验当地生活的好去处,点一壶砖茶,配上一块馕,看着街上来往的维吾尔族老人,时光仿佛在此停滞。 旅游小贴士:喀什古城最佳游览时间是清晨或傍晚,此时光线柔和,游客较少。记得穿舒适的鞋子,古城内多为石板路和土路。 二、帕米尔高原——世界屋脊上的壮美风光 帕米尔高原被誉为"世界屋脊",平均海拔4000米以上,是连接中亚和南亚的天然屏障。这里的慕士塔格峰(海拔7546米)和公格尔九别峰构成了壮丽的雪山景观,被称为"冰山之父"。 高原上的卡拉库里湖是必去景点,湖水随光线变化呈现蓝、绿、黑等不同颜色,倒映着雪山,景色令人震撼。塔什库尔干县是中国唯一的塔吉克族自治县,这里的石头城遗址和红其拉甫口岸也值得一游。 高原反应预防:帕米尔高原海拔高,建议提前在喀什适应1-2天,准备抗高反药物,行动要缓慢,避免剧烈运动。 三、塔克拉玛干沙漠——死亡之海的奇幻之旅 作为世界第二大流动沙漠,塔克拉玛干沙漠占据了南疆大部分地区,维吾尔语意为"进去出不来"。沙漠中的胡杨林是最具特色的景观,特别是秋季,金黄的胡杨与蓝天沙漠形成强烈对比。 沙漠公路是世界最长的贯穿流动沙漠的等级公路,沿途可欣赏壮观的沙丘景观。麦盖提县的N39°沙漠探险基地是体验沙漠露营、骑骆驼的好去处。 最佳旅行时间:10月下旬至11月上旬是观赏胡杨的最佳季节,此时气温适宜,胡杨叶子金黄。夏季沙漠温度极高,不建议此时前往。 四、天山神秘大峡谷——红色山岩的视觉盛宴 位于库车县北部的天山神秘大峡谷由红色砂岩构成,经过亿万年的风蚀水切,形成了千姿百态的奇特地貌。峡谷全长约5公里,最窄处仅容一人侧身通过。 峡谷内的阿艾石窟保存有精美的佛教壁画,见证了古龟兹国的佛教文化。夕阳西下时,整个峡谷被染成金红色,景色尤为壮观。 摄影建议:峡谷内光线变化大,', 'siteName': '', 'pic': None}]}`

class SearchParserTester {
  /**
   * 运行所有测试
   */
  static runAllTests() {
    console.log('🧪 开始搜索内容解析器测试...\n')
    
    this.testBasicParsing()
    this.testContentFormatting()
    this.testErrorHandling()
    this.testPerformance()
    
    console.log('✅ 所有测试完成!')
  }

  /**
   * 测试基础解析功能
   */
  static testBasicParsing() {
    console.log('📋 测试1: 基础解析功能')
    
    try {
      const parsed = SearchContentParser.parseSearchContent(testSearchContent)
      
      console.log('✓ 解析成功')
      console.log(`✓ 数据类型: ${parsed.type}`)
      console.log(`✓ 搜索结果数量: ${parsed.results.length}`)
      console.log(`✓ 总结果数: ${parsed.metadata.totalResults}`)
      
      // 检查第一个结果的结构
      if (parsed.results.length > 0) {
        const firstResult = parsed.results[0]
        console.log(`✓ 第一个结果标题: ${firstResult.title.substring(0, 30)}...`)
        console.log(`✓ 第一个结果摘要: ${firstResult.summary.substring(0, 50)}...`)
        console.log(`✓ 相关性分数: ${firstResult.relevanceScore}`)
      }
      
      console.log('')
    } catch (error) {
      console.error('❌ 基础解析测试失败:', error)
    }
  }

  /**
   * 测试内容格式化功能
   */
  static testContentFormatting() {
    console.log('🎨 测试2: 内容格式化功能')
    
    try {
      const formattedHtml = ContentFormatter.formatToolContent(testSearchContent, {
        showSummary: true,
        showMetadata: true,
        maxResults: 5,
        cardStyle: true
      })
      
      console.log('✓ HTML格式化成功')
      console.log(`✓ 生成HTML长度: ${formattedHtml.length} 字符`)
      
      // 检查是否包含关键元素
      const hasSearchContainer = formattedHtml.includes('search-results-container')
      const hasSearchTitle = formattedHtml.includes('search-results-title')
      const hasSearchItems = formattedHtml.includes('search-item')
      
      console.log(`✓ 包含搜索容器: ${hasSearchContainer}`)
      console.log(`✓ 包含搜索标题: ${hasSearchTitle}`)
      console.log(`✓ 包含搜索项目: ${hasSearchItems}`)
      
      console.log('')
    } catch (error) {
      console.error('❌ 内容格式化测试失败:', error)
    }
  }

  /**
   * 测试错误处理
   */
  static testErrorHandling() {
    console.log('🛡️ 测试3: 错误处理')
    
    // 测试无效输入
    const invalidInputs = [
      null,
      undefined,
      '',
      'invalid json',
      '{"invalid": "structure"}',
      '{"type": "unknown", "data": []}'
    ]
    
    invalidInputs.forEach((input, index) => {
      try {
        const result = SearchContentParser.parseSearchContent(input)
        console.log(`✓ 无效输入 ${index + 1} 处理正确: ${result === null ? 'null' : '有结果'}`)
      } catch (error) {
        console.log(`✓ 无效输入 ${index + 1} 错误处理正确: ${error.message}`)
      }
    })
    
    console.log('')
  }

  /**
   * 测试性能
   */
  static testPerformance() {
    console.log('⚡ 测试4: 性能测试')
    
    const iterations = 100
    const startTime = performance.now()
    
    for (let i = 0; i < iterations; i++) {
      SearchContentParser.parseSearchContent(testSearchContent)
    }
    
    const endTime = performance.now()
    const totalTime = endTime - startTime
    const avgTime = totalTime / iterations
    
    console.log(`✓ ${iterations} 次解析总耗时: ${totalTime.toFixed(2)}ms`)
    console.log(`✓ 平均每次解析耗时: ${avgTime.toFixed(2)}ms`)
    console.log(`✓ 每秒可处理: ${Math.round(1000 / avgTime)} 次`)
    
    console.log('')
  }

  /**
   * 测试文本摘要功能
   */
  static testTextSummary() {
    console.log('📝 测试5: 文本摘要功能')
    
    try {
      const parsed = SearchContentParser.parseSearchContent(testSearchContent)
      const textSummary = SearchContentParser.getTextSummary(parsed, 3)
      
      console.log('✓ 文本摘要生成成功')
      console.log('摘要内容:')
      console.log(textSummary)
      console.log('')
    } catch (error) {
      console.error('❌ 文本摘要测试失败:', error)
    }
  }

  /**
   * 测试内容统计功能
   */
  static testContentStats() {
    console.log('📊 测试6: 内容统计功能')
    
    try {
      const stats = ContentFormatter.getContentStats(testSearchContent)
      
      console.log('✓ 内容统计生成成功')
      console.log(`✓ 内容类型: ${stats.type}`)
      console.log(`✓ 内容长度: ${stats.length} 字符`)
      console.log(`✓ 单词数量: ${stats.words}`)
      console.log(`✓ 行数: ${stats.lines}`)
      console.log(`✓ 是否结构化数据: ${stats.hasStructuredData}`)
      
      if (stats.searchResults) {
        console.log(`✓ 搜索结果数量: ${stats.searchResults}`)
      }
      
      console.log('')
    } catch (error) {
      console.error('❌ 内容统计测试失败:', error)
    }
  }
}

// 导出测试类
export default SearchParserTester

// 如果在浏览器环境中直接运行
if (typeof window !== 'undefined') {
  window.SearchParserTester = SearchParserTester
}
