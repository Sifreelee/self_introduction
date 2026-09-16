/* ═══════════════════════════════════════════════════════════════════
   ★ 欢迎来到内容配置文件 ★
   ─────────────────────────────────────────────────────────────────
   您以后只需要修改这一个文件，即可更新全站文字内容。
   图片放到 assets/images 文件夹，视频放到 assets/videos 文件夹，
   然后把文件名填写到对应位置即可，详见《使用说明.md》。

   修改规则：
   · 只改引号 "" 里面的文字，注意别删掉引号和逗号
   · 想少显示一张照片/一篇随笔，删除对应 { ... } 整段即可
   · 想新增，复制一段 { ... }，改掉内容，注意与前一段之间用逗号隔开
   ═══════════════════════════════════════════════════════════════════ */

const SITE_DATA = {

  /* ─────────── 卷首（首页大标题区） ─────────── */
  site: {
    name: "洛晴跃飞",          // 导航栏与浏览器标题处的名字
    seal: "荔",               // 导航左侧印章上的一个字
    heroTitle: "洛晴跃飞",      // 首屏竖排大标题（建议 2 ~ 4 字）
    heroSeal: "絲芙荔行跡",       // 竖排大标题旁的印章文字（建议 2 ~ 4 字）
    heroQuote: "人生如逆旅，我亦是行人",   // 首屏诗句
    heroSub: "一个人的行走、记录与热爱",     // 首屏小字副标题
    footerMotto: "诗意趁年华", // 页脚竖排诗句
    footerText: "© 洛晴跃飞·享受自然，热爱生活",  // 页脚版权行
    contactPoem: "愿以随性之名·与君相遇",   // 相邀区主标题
    contactSub: "若想聊聊旅行、摄影或茶饭闲事，欢迎随时来敲门!",  // 相邀区副标题
    photoSeal: "影"          // 照片集图集卡片鼠标悬浮时浮现的朱红印章文字（建议 1 个字，不填则默认「影」）
  },

  /* ─────────── 壹 · 其人（个人简介） ─────────── */
  profile: {
    name: "丝芙荔",            // 您的名字
    enName: "Sifree",   // 拼音或英文名
    portrait: "assets/images/gerenzhaopian.jpg",  // 肖像照片路径（换成您的照片文件名）
    portraitCaption: "摄影中",   // 肖像上的小签条文字
    // 身份标签，可增删
    tags: ["旅行爱好者", "摄影初学者", "文博爱好者", "古建研究小白"],
    // 简介段落，一段一个 ""，想加段落就按格式续写
    bio: [
      "得闲便背起相机，去人少的山径走一走。相信天地有大美而不言，愿意做那个替山水说话的人。",
      "这些年去过一些地方，看过重庆的雾，更看过东北的雪。每一段路都值得被记住，于是有了这个小站—记录行走的点滴，分享旅途的风景。"
    ],
    // 底部数据条：数字 + 说明，可自行更换内容
    stats: [
      { num: "5+", label: "行走年头" },
      { num: "32+", label: "抵达城市" },
      { num: "30000+", label: "快门次数" },
      { num: "∞", label: "热爱程度" }
    ]
  },

  /* ─────────── 贰 · 行迹 之 旅行随笔 ───────────
     cover: 配图路径，照片放 assets/images 后把文件名写在这里
     content: 正文，一段一个 "" */
  travel: [
    {
      title: "茶啊冲往事",
      place: "吉林 · 长春",
      date: "2021-09",
      cover: "assets/images/trip-1.jpg",
      excerpt: "茶啊冲往事，长春的秋天是金色的。走在南湖公园的林荫道上，落叶铺满了脚下的路。阳光透过枝叶洒在身上，暖得像一杯刚泡好的龙井。",
      content: [
        "第一次背井离乡",
        "南湖的风。",
        "净月潭的水。",
        "忘不掉的大学时光。",
        "难忘怀的第二故乡。"
      ]
    },
    {
      title: "雾都记录簿",
      place: "中国 · 重庆",
      date: "2025-09",
      cover: "assets/images/trip-2.jpg",
      excerpt: "山城的雾是有温度的。清晨，雾气从江面升起，像一条白色的绸带，把整座城市裹在柔软的怀里。走在鹅卵石铺就的老街上，脚下的水声和远处的钟声交织成一首低沉的乐章。",
      content: [
        "嘞是雾都！",
        "永远爱重庆。",
        "热情的土地孕育热情的人。",
        "重庆的冬天忧郁又温润。",
        "江水缓缓流淌，船只穿梭其间，灯火映照在水面上，闪烁着温暖的光。"
      ]
    },
        {
      title: "北平半载",
      place: "中国 • 北京",
      date: "2026-08",
      cover: "assets/images/trip-3.jpg",
      excerpt: "北平之行。",
      content: [
        "北平结缘",
        "机缘巧合，我到了北京。",
        "嗅到了历史的芬芳。",
        "圆了我的古建梦。"
      ]
    },
  ],

  /* ─────────── 贰 · 行迹 之 照片集（图集，按城市分组） ───────────
     每个城市是一个图集 { city, cover, photos: [...] }：
       · city：城市名
       · photos：该城市的照片数组，每张 { src, title }
       · seal：（可选）这个城市专属的悬浮印章文字，不写就用上面 site.photoSeal 的统一文字
     想加新城市/新照片，复制一段照着改即可。
     照片放进 assets/images 文件夹。 */
  photos: [
     {
      city: "镇馆之宝",
      seal: "珍",
      photos: [
        { src: "assets/images/bowu1.jpg", title: "国家博物馆" },
        { src: "assets/images/bowu2.jpg", title: "首都博物馆" },
        { src: "assets/images/bowu3.jpg", title: "辽宁省博物馆" },
        { src: "assets/images/bowu4.jpg", title: "湖北省博物馆" },
        { src: "assets/images/bowu5.jpg", title: "吉林省博物馆" }
      ]
    },
     {
      city: "中国 北京",
      seal: "京",
      photos: [
        { src: "assets/images/travel-28.jpg", title: "古今同框：中国尊故宫" },
        { src: "assets/images/travel-29.jpg", title: "雍和宫" },
        { src: "assets/images/travel-30.jpg", title: "中山公园 中山堂：社稷坛" },
        { src: "assets/images/travel-31.jpg", title: "颐和园 谐趣园" },
        { src: "assets/images/travel-32.jpg", title: "颐和园 佛香阁" },
        { src: "assets/images/travel-33.jpg", title: "天坛祈年殿" },
        { src: "assets/images/travel-34.jpg", title: "圜丘坛" },
        { src: "assets/images/travel-35.jpg", title: "西开教堂" },
        { src: "assets/images/travel-36.jpg", title: "太庙大殿" },
        { src: "assets/images/travel-37.jpg", title: "东交民巷" },
        { src: "assets/images/travel-38.jpg", title: "方泽坛" },
        { src: "assets/images/travel-39.jpg", title: "国子监街" },
        { src: "assets/images/travel-40.jpg", title: "中轴线北望" },
        { src: "assets/images/travel-41.jpg", title: "中轴线南望" },
        { src: "assets/images/travel-42.jpg", title: "天坛俯拍远景" },
        { src: "assets/images/travel-43.jpg", title: "圜丘坛与回音壁" },
        { src: "assets/images/travel-44.jpg", title: "北海之夏" }
      ]
    },
    {
      city: "中国 重庆",
      seal: "渝",          // 本图集专属印章字（不想要就删掉这一行，会统一用 site.photoSeal）
      photos: [
        { src: "assets/images/travel-16.jpg", title: "嘉陵江意" },
        { src: "assets/images/travel-17.jpg", title: "长江国际" },
        { src: "assets/images/travel-18.jpg", title: "南岸夜潮" },
        { src: "assets/images/travel-19.jpg", title: "川美后街" },
        { src: "assets/images/travel-20.jpg", title: "南川金佛山登山处" },
        { src: "assets/images/travel-21.jpg", title: "金佛山云海" }
      ]
    },
    {
      city: "山东 淄博",
      seal: "淄", 
      photos: [
        { src: "assets/images/travel-13.jpg", title: "四宝山俯拍" },
        { src: "assets/images/travel-14.jpg", title: "叹淄景" }
      ]
    },
    {
      city: "辽宁 沈阳",
      seal: "沈",
      photos: [
        { src: "assets/images/travel-4.jpg", title: "北陵公园" }
      ]
    },
    {
      city: "江苏 徐州",
      seal: "彭",
      photos: [
        { src: "assets/images/travel-5.jpg", title: "户部山" }
      ]
    },
    {
      city: "山东 泰安",
      seal: "泰",
      photos: [
        { src: "assets/images/travel-6.jpg", title: "泰山 南天门" }
      ]
    },
    {
      city: "山东 青州",
      seal: "青",
      photos: [
        { src: "assets/images/travel-7.jpg", title: "青州古城落日" }
      ]
    },
    {
      city: "吉林 长春",
      seal: "长",
      photos: [
        { src: "assets/images/travel-8.jpg", title: "净月潭" }
      ]
    },
    {
      city: "辽宁 大连",
      seal: "连",
      photos: [
        { src: "assets/images/travel-9.jpg", title: "星海广场" },
        { src: "assets/images/travel-26.jpg", title: "莲花山顶" },
        { src: "assets/images/travel-27.jpg", title: "渔人码头" }
      ]
    },
    {
      city: "湖北 武汉",
      seal: "汉",
      photos: [
        { src: "assets/images/travel-10.jpg", title: "黄鹤楼之夜" }
      ]
    },
    {
      city: "中国 天津",
      seal: "津",
      photos: [
        { src: "assets/images/travel-11.jpg", title: "津湾广场" }
      ]
    },
    {
      city: "江苏 连云港",
      seal: "海",
      photos: [
        { src: "assets/images/travel-12.jpg", title: "在海一方公园" }
      ]
    },
    {
      city: "四川 成都",
      seal: "蓉",
      photos: [
        { src: "assets/images/travel-15.jpg", title: "天府广场" },
        { src: "assets/images/travel-25.jpg", title: "青羊宫" }
      ]
    },
    {
      city: "黑龙江 哈尔滨",
      seal: "哈",
      photos: [
        { src: "assets/images/travel-22.jpg", title: "中央大街" }
      ]
    },
    {
      city: "山东 济南",
      seal: "济",
      photos: [
        { src: "assets/images/travel-23.jpg", title: "曲水亭街" },
        { src: "assets/images/travel-24.jpg", title: "胶济铁路博物馆" }
      ]
    }
  ],

  /* ─────────── 贰 · 行迹 之 影像集（社交视频平台入口） ───────────
     点击卡片直接跳转到对应平台主页。
     name: 平台名；desc: 一句话说明；link: 平台主页链接 */
  social: [
    { name: "抖音", desc: "我的旅行与日常短视频", link: "https://v.douyin.com/0_a546z2xug/" },
    { name: "小红书", desc: "图文笔记与攻略分享", link: "https://xhslink.cn/o/8HhwbL6wKRb" },
    { name: "Bilibili", desc: "学习资料干货分享", link: "https://b23.tv/t9qoj72" },
    { name: "Instagram", desc: "摄影作品与行迹瞬间", link: "https://www.instagram.com/sifree_lee?stkn=MWw1YXBscWVxMTEweA==" }
  ],

  /* ─────────── 点亮中国 · 去过的城市 ───────────
    
     【填写规则】每行一个城市，有两种写法：

     ① 只写城市名（自动识别省份）：
         "西安"   → 系统自动识别为「陕西」并点亮陕西省
         "济南"   → 自动识别为「山东」
         —— 系统内置「城市→省份」对照表（约 150 个主要城市）。

     ② 显式指定省份（推荐，尤其小众地名）：
         写成 "城市名@省份"，用 @ 隔开。例如：
         "凤凰@湖南"  → 直接点亮湖南省，不受对照表限制
         "漠河@黑龙江" → 显式指定
         任何对照表里没有的小众地名，用这种写法最稳。

     【直辖市 / 特别行政区】城市名本身就是省级，直接写城市名即可，
        弹窗里的小字会自动显示「中国」（而不是重复城市名）：
         "北京"、"天津"、"上海"、"重庆"、"香港"、"澳门"。

     想新增城市：复制一行，注意逗号隔开。
     想删除城市：删除对应整行即可。
     「抵达城市」数字自动 = 下面城市数量，无需手动改。 */
  cities: [
    "北京", "天津", "长春", "沈阳", "哈尔滨",
    "大连", "济南", "淄博", "泰安", "青州",
    "徐州", "连云港", "成都", "重庆", "武汉", "大同","武威@甘肃"
  ],

  /* ─────────── 叁 · 所好（个人爱好） ───────────
     icon 可选值：brush(毛笔) camera(相机) tea(茶) mountain(登山)
                 book(书) guqin(琴) chess(棋) flower(花) music(乐) run(跑) */
  hobbies: [
    {
      name: "写作",
      en: "WRITING",
      icon: "brush",
      desc: "摘抄、记录、分享。"
    },
    {
      name: "摄影",
      en: "PHOTOGRAPHY",
      icon: "camera",
      desc: "定格自然与烟火气。"
    },
    {
      name: "品茶",
      en: "TEA CEREMONY",
      icon: "tea",
      desc: "春饮花，夏饮绿，秋饮乌龙，冬饮熟普。"
    },
    {
      name: "徒步",
      en: "HIKING",
      icon: "mountain",
      desc: "尝试感受自我的来源。"
    },
    {
      name: "阅读",
      en: "READING",
      icon: "book",
      desc: "徜徉文字的世界。"
    },
    {
      name: "复古",
      en: "VINTAGE",
      icon: "guqin",
      desc: "HIPHOP、LO-FI、R&B、JAZZ、FUNK！！"
    },
    {
      name: "游戏",
      en: "GAME",
      icon: "chess",
      desc: "OVERWATCH、LOL、Cyberpunk2077。"
    },
    {
      name: "集邮",
      en: "STAMP",
      icon: "stamp",
      desc: "方寸之间，藏尽山河岁月。"
    }
  ],

  /* ─────────── 肆 · 相邀（联系方式） ───────────
     label 名称，value 账号/说明，link 跳转链接（没有就留空 ""）
     社交平台只填 label 和 link：把 link 改成你自己的主页网址，
     页面上这个名字就会变成可点击的链接。 */
  contact: [
    { label: "邮箱", value: "1582763936@qq.com", link: "mailto:1582763936@qq.com" },
    { label: "微信", value: "yisorelfd", link: "" },
    { label: "坐标", value: "山东·淄博", link: "" },
    { label: "抖音", value: "热爱生活的保暖裤", link: "https://v.douyin.com/0_a546z2xug/" },
    { label: "Bilibili", value: "热爱生活的丝芙荔", link: "https://b23.tv/t9qoj72" },
    { label: "小红书", value: "丝芙荔", link: "https://xhslink.cn/o/8HhwbL6wKRb" },
    { label: "微博", value: "丝芙荔", link: "https://weibo.com/u/6128243925" },
    { label: "网易云", value: "热爱生活的保暖裤", link: "https://y.music.163.com/m/user?id=408620011" },
    { label: "Instagram", value: "sifree_lee", link: "https://www.instagram.com/sifree_lee?stkn=MWw1YXBscWVxMTEweA==" }
  ]
};
