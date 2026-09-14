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
    contactSub: "若想聊聊旅行、摄影或茶饭闲事，欢迎随时来敲门!"  // 相邀区副标题
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
      "这些年去过一些地方，看过重庆的雾、东北的雪。每一段路都值得被记住，于是有了这个小站——记录行走的点滴，分享旅途的风景。"
    ],
    // 底部数据条：数字 + 说明，可自行更换内容
    stats: [
      { num: "5+", label: "行走年头" },
      { num: "32", label: "抵达城市" },
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
        "忘不掉的大学时光",
        "难忘怀的第二故乡"
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
        "热情的土地孕育热情的人",
        "夏天的闷热和冬天的湿冷都无法阻挡我对这座城市的热爱。雾气弥漫的早晨，走在解放碑的街头，仿佛置身于一幅水墨画中。",
        "江水缓缓流淌，船只穿梭其间，灯火映照在水面上，闪烁着温暖的光。"
      ]
    },
        {
      title: "北平半载",
      place: "中国 • 北京",
      date: "2026-08",
      cover: "assets/images/trip-3.png",
      excerpt: "北平之行。",
      content: [
        "北平结缘",
        "机缘巧合，我到了北京。",
        "嗅到了历史的芬芳。",
        "圆了我的古建梦。"
      ]
    },
  ],

  /* ─────────── 贰 · 行迹 之 照片集 ───────────
     src: 照片路径。把照片放进 assets/images，文件名写在这里即可。
     目前展示的是示例水墨占位图，替换后即为您的照片。 */
  photos: [
    { src: "assets/images/travel-4.jpg", title: "北陵公园", place: "辽宁·沈阳" },
    { src: "assets/images/travel-5.jpg", title: "户部山", place: "江苏·徐州" },
    { src: "assets/images/travel-6.jpg", title: "泰山 南天门", place: "山东·泰安" },
    { src: "assets/images/travel-7.jpg", title: "青州古城落日", place: "山东·青州市" },
    { src: "assets/images/travel-8.jpg", title: "净月潭", place: "吉林·长春" },
    { src: "assets/images/travel-9.jpg", title: "星海广场", place: "辽宁·大连" },
    { src: "assets/images/travel-10.jpg", title: "黄鹤楼之夜", place: "湖北·武汉" },
    { src: "assets/images/travel-11.jpg", title: "津湾广场", place: "中国·天津" },
    { src: "assets/images/travel-12.jpg", title: "在海一方公园", place: "江苏·连云港" },
    { src: "assets/images/travel-13.jpg", title: "四宝山俯拍", place: "山东·淄博" },
    { src: "assets/images/travel-14.jpg", title: "叹淄景", place: "山东·淄博" },
    { src: "assets/images/travel-15.jpg", title: "天府广场", place: "四川·成都" },
    { src: "assets/images/travel-16.jpg", title: "嘉陵江意", place: "中国·重庆" },
    { src: "assets/images/travel-17.jpg", title: "长江国际", place: "中国·重庆" },
    { src: "assets/images/travel-18.jpg", title: "南岸夜潮", place: "中国·重庆" },
    { src: "assets/images/travel-19.jpg", title: "川美后街", place: "中国·重庆" },
    { src: "assets/images/travel-20.jpg", title: "南川金佛山登山处", place: "中国·重庆" },
    { src: "assets/images/travel-21.jpg", title: "金佛山云海", place: "中国·重庆" },
    
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
      name: "赏花",
      en: "FLOWER",
      icon: "flower",
      desc: "模拟蜜蜂。"
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
