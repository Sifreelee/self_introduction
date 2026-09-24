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
      { num: "∞", label: "爱好广泛度" }
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
       · desc：相册简介（早期写法，仅作兜底）。
               正式内容统一写在 js/album-desc.js —— 那里不用管 JS 语法，
               在「### 相册名」下面直接填字就行，不限字数、空行分段，网页上不可修改。
               两边都写了的话，以 js/album-desc.js 为准。
       · photos：该城市的照片数组，每张 { src, title }
       · seal：这个城市专属的悬浮印章文字，不写就用上面 site.photoSeal 的统一文字
       · star：星标。设为 true 时，这本图集封面左上角会出现一枚
              「圆形铜钱」样式的中式标记（深朱色，低透明度，低调不抢眼）。
              想给某个图集加星标，就在那段里写一行  star: true,
              想取消就删掉这行（或改成 star: false）。
       · tags：自定义标签（圆角小框），写在 photos 前面，例如
              tags: ["镇馆之宝", "青铜器", "佛教文物"],
              点开图集后标题下方会出现一排圆角小框，点哪个就只显示
              「照片名中含有该标签」的照片，再点一次取消。
              照片名 = 网页上显示的名字，即每张照片的 title；
              源文件名不参与匹配（title 没写时才用它兜底）。不区分大小写。
              不写就没有这一排小框。
    */
  photos: [ 
     {
      city: "文物介绍及科普",
      desc: "可搜索下列文物标签进行类别区分，琉璃、钱币等尚未更新。古建筑相关的形制与构件见下方相册。",
      seal: "珍",
      star: true, 
      tags: ["镇馆之宝", "青铜器", "陶瓷", "金银器", "玉器", "佛教文物", "三星堆"],
      photos: [
      { src: "assets/images/bowu/zgzb/1001.jpg", title: "国家博物馆 镇馆之宝" },
        { src: "assets/images/bowu/zgzb/1002.jpg", title: "首都博物馆 镇馆之宝" },
        { src: "assets/images/bowu/zgzb/1003.jpg", title: "辽宁省博物馆 镇馆之宝" },
        { src: "assets/images/bowu/zgzb/1004.jpg", title: "湖北省博物馆 镇馆之宝" },
        { src: "assets/images/bowu/zgzb/1005.jpg", title: "吉林省博物馆 镇馆之宝" },
        { src: "assets/images/bowu/zgzb/1006.jpg", title: "四川省博物馆 镇馆之宝" },
      { src: "assets/images/bowu/qtq/青铜器 北京非遗工艺博 其他 凤舞冠 服饰器.jpg", title: "青铜器 北京非遗工艺博 其他 凤舞冠 服饰器" },
        { src: "assets/images/bowu/qtq/青铜器 吉林省博 东汉 错金银丙午神钩铜带钩 服饰器.jpg", title: "青铜器 吉林省博 东汉 错金银丙午神钩铜带钩 服饰器" },
        { src: "assets/images/bowu/qtq/青铜器 吉林省博 汉代 夫余鎏金铜面具 供奉像.jpg", title: "青铜器 吉林省博 汉代 夫余鎏金铜面具 供奉像" },
        { src: "assets/images/bowu/qtq/青铜器 四川省博 战国 嵌错宴乐水陆攻战纹铜壶 盛酒器.jpg", title: "青铜器 四川省博 战国 嵌错宴乐水陆攻战纹铜壶 盛酒器" },
        { src: "assets/images/bowu/qtq/青铜器 四川省博 西周 蟠龙盖兽面纹铜罍 盛酒器.jpg", title: "青铜器 四川省博 西周 蟠龙盖兽面纹铜罍 盛酒器" },
        { src: "assets/images/bowu/qtq/青铜器 四川省博 西周 象首耳卷体夔纹铜罍 盛酒器.jpg", title: "青铜器 四川省博 西周 象首耳卷体夔纹铜罍 盛酒器" },
        { src: "assets/images/bowu/qtq/青铜器 国博 其他 孝靖皇后三龙二凤冠仿 服饰器.jpg", title: "青铜器 国博 其他 孝靖皇后三龙二凤冠仿 服饰器" },
        { src: "assets/images/bowu/qtq/青铜器 国博 其他 隋炀帝萧皇后冠饰复原 服饰器.jpg", title: "青铜器 国博 其他 隋炀帝萧皇后冠饰复原 服饰器" },
        { src: "assets/images/bowu/qtq/青铜器 国博 商代 三星堆青铜人头像 祭祀用器.jpg", title: "青铜器 国博 商代 三星堆青铜人头像 祭祀用器" },
        { src: "assets/images/bowu/qtq/青铜器 国博 商代 三星堆青铜尊 盛酒器.jpg", title: "青铜器 国博 商代 三星堆青铜尊 盛酒器" },
        { src: "assets/images/bowu/qtq/青铜器 国博 商代 古蜀三星堆青铜面具 祭祀用器.jpg", title: "青铜器 国博 商代 古蜀三星堆青铜面具 祭祀用器" },
        { src: "assets/images/bowu/qtq/青铜器 国博 商代 四羊方尊 盛酒器.jpg", title: "青铜器 国博 商代 四羊方尊 盛酒器" },
        { src: "assets/images/bowu/qtq/青铜器 国博 商代 妇好青铜方尊 盛酒器.jpg", title: "青铜器 国博 商代 妇好青铜方尊 盛酒器" },
        { src: "assets/images/bowu/qtq/青铜器 国博 商代 妇好青铜方斝 温酒器.jpg", title: "青铜器 国博 商代 妇好青铜方斝 温酒器" },
        { src: "assets/images/bowu/qtq/青铜器 国博 商代 妇好青铜瓿 盛贮器.jpg", title: "青铜器 国博 商代 妇好青铜瓿 盛贮器" },
        { src: "assets/images/bowu/qtq/青铜器 国博 商代 龙虎青铜尊 盛酒器.jpg", title: "青铜器 国博 商代 龙虎青铜尊 盛酒器" },
        { src: "assets/images/bowu/qtq/青铜器 国博 待定 刚放进去的青铜匜 盥洗水器.jpg", title: "青铜器 国博 待定 刚放进去的青铜匜 盥洗水器" },
        { src: "assets/images/bowu/qtq/青铜器 国博 待定 青铜罍 盛酒器.jpg", title: "青铜器 国博 待定 青铜罍 盛酒器" },
        { src: "assets/images/bowu/qtq/青铜器 国博 战国 令狐君嗣子青铜壶 盛酒器.jpg", title: "青铜器 国博 战国 令狐君嗣子青铜壶 盛酒器" },
        { src: "assets/images/bowu/qtq/青铜器 国博 战国 虎钮青铜錞于 军乐器.jpg", title: "青铜器 国博 战国 虎钮青铜錞于 军乐器" },
        { src: "assets/images/bowu/qtq/青铜器 国博 战国 错金银马首形青铜軏 车马器.jpg", title: "青铜器 国博 战国 错金银马首形青铜軏 车马器" },
        { src: "assets/images/bowu/qtq/青铜器 国博 战国 错银卧牛青铜镇 生活用器.jpg", title: "青铜器 国博 战国 错银卧牛青铜镇 生活用器" },
        { src: "assets/images/bowu/qtq/青铜器 国博 战国 青铜冰鉴 冰镇水器.jpg", title: "青铜器 国博 战国 青铜冰鉴 冰镇水器" },
        { src: "assets/images/bowu/qtq/青铜器 国博 明代 孝端皇后九龙九凤冠真 服饰器.jpg", title: "青铜器 国博 明代 孝端皇后九龙九凤冠真 服饰器" },
        { src: "assets/images/bowu/qtq/青铜器 国博 明代 针灸铜人 医用器.jpg", title: "青铜器 国博 明代 针灸铜人 医用器" },
        { src: "assets/images/bowu/qtq/青铜器 国博 春秋 兽耳青铜壶 盛酒器.jpg", title: "青铜器 国博 春秋 兽耳青铜壶 盛酒器" },
        { src: "assets/images/bowu/qtq/青铜器 国博 春秋 晋国青铜方壶 盛酒器.jpg", title: "青铜器 国博 春秋 晋国青铜方壶 盛酒器" },
        { src: "assets/images/bowu/qtq/青铜器 国博 春秋 栾书青铜缶 冰镇水器.jpg", title: "青铜器 国博 春秋 栾书青铜缶 冰镇水器" },
        { src: "assets/images/bowu/qtq/青铜器 国博 春秋 王子午鼎 烹饪盛食器.jpg", title: "青铜器 国博 春秋 王子午鼎 烹饪盛食器" },
        { src: "assets/images/bowu/qtq/青铜器 国博 春秋 虎钮青铜罍 盛酒器.jpg", title: "青铜器 国博 春秋 虎钮青铜罍 盛酒器" },
        { src: "assets/images/bowu/qtq/青铜器 国博 春秋 郑兽钮青铜镈 乐器.jpg", title: "青铜器 国博 春秋 郑兽钮青铜镈 乐器" },
        { src: "assets/images/bowu/qtq/青铜器 国博 春秋 青铜牺尊 盛酒器.jpg", title: "青铜器 国博 春秋 青铜牺尊 盛酒器" },
        { src: "assets/images/bowu/qtq/青铜器 国博 西周 利簋 盛食器.jpg", title: "青铜器 国博 西周 利簋 盛食器" },
        { src: "assets/images/bowu/qtq/青铜器 国博 西周 大盂鼎 烹饪盛食器.jpg", title: "青铜器 国博 西周 大盂鼎 烹饪盛食器" },
        { src: "assets/images/bowu/qtq/青铜器 国博 西周 小臣宅青铜簋 盛食器.jpg", title: "青铜器 国博 西周 小臣宅青铜簋 盛食器" },
        { src: "assets/images/bowu/qtq/青铜器 国博 西周 盠青铜方彝 盛酒器.jpg", title: "青铜器 国博 西周 盠青铜方彝 盛酒器" },
        { src: "assets/images/bowu/qtq/青铜器 国博 西周 虢季子白青铜盘 盥洗水器.jpg", title: "青铜器 国博 西周 虢季子白青铜盘 盥洗水器" },
        { src: "assets/images/bowu/qtq/青铜器 国博 西周 青铜驹尊 盛酒器.jpg", title: "青铜器 国博 西周 青铜驹尊 盛酒器" },
        { src: "assets/images/bowu/qtq/青铜器 国博 西周 颂青铜壶 盛酒器.jpg", title: "青铜器 国博 西周 颂青铜壶 盛酒器" },
        { src: "assets/images/bowu/qtq/青铜器 国博 西汉 七牛虎耳青铜贮贝器 贮贝器.jpg", title: "青铜器 国博 西汉 七牛虎耳青铜贮贝器 贮贝器" },
        { src: "assets/images/bowu/qtq/青铜器 国博 西汉 五牛铜枕 生活用器.jpg", title: "青铜器 国博 西汉 五牛铜枕 生活用器" },
        { src: "assets/images/bowu/qtq/青铜器 国博 西汉 贡纳场面青铜贮贝器 贮贝器.jpg", title: "青铜器 国博 西汉 贡纳场面青铜贮贝器 贮贝器" },
        { src: "assets/images/bowu/qtq/青铜器 国博 西汉 错金银云纹青铜犀尊 盛酒器.jpg", title: "青铜器 国博 西汉 错金银云纹青铜犀尊 盛酒器" },
        { src: "assets/images/bowu/qtq/青铜器 国博 西汉 错金银鸟篆文青铜壶 盛酒器.jpg", title: "青铜器 国博 西汉 错金银鸟篆文青铜壶 盛酒器" },
        { src: "assets/images/bowu/qtq/青铜器 天津市博 西周 太保鼎 烹饪盛食器.jpg", title: "青铜器 天津市博 西周 太保鼎 烹饪盛食器" },
        { src: "assets/images/bowu/qtq/青铜器 徐州博 商代 三星堆平顶青铜人头像吉金万里 祭祀用器.jpg", title: "青铜器 徐州博 商代 三星堆平顶青铜人头像吉金万里 祭祀用器" },
        { src: "assets/images/bowu/qtq/青铜器 徐州博 商代 三星堆青铜人面具 祭祀用器.jpg", title: "青铜器 徐州博 商代 三星堆青铜人面具 祭祀用器" },
        { src: "assets/images/bowu/qtq/青铜器 成都市博 商代 青铜人头像 祭祀用器.jpg", title: "青铜器 成都市博 商代 青铜人头像 祭祀用器" },
        { src: "assets/images/bowu/qtq/青铜器 湖北省博 战国 曾侯乙编钟 乐器.jpg", title: "青铜器 湖北省博 战国 曾侯乙编钟 乐器" },
        { src: "assets/images/bowu/qtq/青铜器 湖北省博 战国 曾侯乙铜鉴缶 冰镇水器.jpg", title: "青铜器 湖北省博 战国 曾侯乙铜鉴缶 冰镇水器" },
        { src: "assets/images/bowu/qtq/青铜器 湖北省博 战国 曾侯乙青铜尊盘 盛酒器.jpg", title: "青铜器 湖北省博 战国 曾侯乙青铜尊盘 盛酒器" },
        { src: "assets/images/bowu/qtq/青铜器 湖北省博 战国 曾侯乙青铜建鼓座 乐器.jpg", title: "青铜器 湖北省博 战国 曾侯乙青铜建鼓座 乐器" },
        { src: "assets/images/bowu/qtq/青铜器 湖北省博 春秋 越王勾践剑 兵器.jpg", title: "青铜器 湖北省博 春秋 越王勾践剑 兵器" },
        { src: "assets/images/bowu/qtq/青铜器 考古博 商代 三星堆青铜人面具 祭祀用器.jpg", title: "青铜器 考古博 商代 三星堆青铜人面具 祭祀用器" },
        { src: "assets/images/bowu/qtq/青铜器 考古博 商代 兽面纹铜觯 饮酒器.jpg", title: "青铜器 考古博 商代 兽面纹铜觯 饮酒器" },
        { src: "assets/images/bowu/qtq/青铜器 考古博 商代 凤鸟纹青铜提梁卣 盛酒器.jpg", title: "青铜器 考古博 商代 凤鸟纹青铜提梁卣 盛酒器" },
        { src: "assets/images/bowu/qtq/青铜器 考古博 商代 史铜觯 饮酒器.jpg", title: "青铜器 考古博 商代 史铜觯 饮酒器" },
        { src: "assets/images/bowu/qtq/青铜器 考古博 商代 司兔丂母癸铜方尊 盛酒器.jpg", title: "青铜器 考古博 商代 司兔丂母癸铜方尊 盛酒器" },
        { src: "assets/images/bowu/qtq/青铜器 考古博 商代 司兔丂母铜圆尊 盛酒器.jpg", title: "青铜器 考古博 商代 司兔丂母铜圆尊 盛酒器" },
        { src: "assets/images/bowu/qtq/青铜器 考古博 商代 司兔丂母铜方壶 盛酒器.jpg", title: "青铜器 考古博 商代 司兔丂母铜方壶 盛酒器" },
        { src: "assets/images/bowu/qtq/青铜器 考古博 商代 司巧母铜方壶 盛酒器.jpg", title: "青铜器 考古博 商代 司巧母铜方壶 盛酒器" },
        { src: "assets/images/bowu/qtq/青铜器 考古博 商代 回纹青铜甗 蒸食器.jpg", title: "青铜器 考古博 商代 回纹青铜甗 蒸食器" },
        { src: "assets/images/bowu/qtq/青铜器 考古博 商代 妇好圈足铜觥 青铜礼器.jpg", title: "青铜器 考古博 商代 妇好圈足铜觥 青铜礼器" },
        { src: "assets/images/bowu/qtq/青铜器 考古博 商代 妇好夔足铜鼎 烹饪盛食器.jpg", title: "青铜器 考古博 商代 妇好夔足铜鼎 烹饪盛食器" },
        { src: "assets/images/bowu/qtq/青铜器 考古博 商代 妇好铜方彝 盛酒器.jpg", title: "青铜器 考古博 商代 妇好铜方彝 盛酒器" },
        { src: "assets/images/bowu/qtq/青铜器 考古博 商代 妇好铜方斝 温酒器.jpg", title: "青铜器 考古博 商代 妇好铜方斝 温酒器" },
        { src: "assets/images/bowu/qtq/青铜器 考古博 商代 妇好铜方罍 盛酒器.jpg", title: "青铜器 考古博 商代 妇好铜方罍 盛酒器" },
        { src: "assets/images/bowu/qtq/青铜器 考古博 商代 妇好龙头提梁铜卣 盛酒器.jpg", title: "青铜器 考古博 商代 妇好龙头提梁铜卣 盛酒器" },
        { src: "assets/images/bowu/qtq/青铜器 考古博 商代 青铜盉 调酒注水器.jpg", title: "青铜器 考古博 商代 青铜盉 调酒注水器" },
        { src: "assets/images/bowu/qtq/青铜器 考古博 商代 青铜跪坐人像 祭祀用器.jpg", title: "青铜器 考古博 商代 青铜跪坐人像 祭祀用器" },
        { src: "assets/images/bowu/qtq/青铜器 考古博 待定 铜甗 蒸食器.jpg", title: "青铜器 考古博 待定 铜甗 蒸食器" },
        { src: "assets/images/bowu/qtq/青铜器 考古博 西周 早期蛇纹铜卣 盛酒器.jpg", title: "青铜器 考古博 西周 早期蛇纹铜卣 盛酒器" },
        { src: "assets/images/bowu/qtq/青铜器 考古博 西周 邓仲牺尊 盛酒器.jpg", title: "青铜器 考古博 西周 邓仲牺尊 盛酒器" },
        { src: "assets/images/bowu/qtq/青铜器 辽宁省博 商代 饕餮纹大圆鼎 烹饪盛食器.jpg", title: "青铜器 辽宁省博 商代 饕餮纹大圆鼎 烹饪盛食器" },
        { src: "assets/images/bowu/qtq/青铜器 辽宁省博 西周 卷体夔纹蟠龙盖罍 盛酒器.jpg", title: "青铜器 辽宁省博 西周 卷体夔纹蟠龙盖罍 盛酒器" },
        { src: "assets/images/bowu/qtq/青铜器 辽宁省博 西周 圉簋 盛食器.jpg", title: "青铜器 辽宁省博 西周 圉簋 盛食器" },
        { src: "assets/images/bowu/qtq/青铜器 重庆三峡博 商代 三羊铜尊 盛酒器.jpg", title: "青铜器 重庆三峡博 商代 三羊铜尊 盛酒器" },
        { src: "assets/images/bowu/qtq/青铜器 重庆三峡博 战国 凤鸟纹错银铜壶 盛酒器.jpg", title: "青铜器 重庆三峡博 战国 凤鸟纹错银铜壶 盛酒器" },
        { src: "assets/images/bowu/qtq/青铜器 重庆三峡博 战国 虎纹青铜戈 兵器.jpg", title: "青铜器 重庆三峡博 战国 虎纹青铜戈 兵器" },
        { src: "assets/images/bowu/qtq/青铜器 重庆三峡博 战国 虎钮錞于 军乐器.jpg", title: "青铜器 重庆三峡博 战国 虎钮錞于 军乐器" },
        { src: "assets/images/bowu/qtq/青铜器 重庆三峡博 战国 青铜鸟形尊 盛酒器.jpg", title: "青铜器 重庆三峡博 战国 青铜鸟形尊 盛酒器" },
        { src: "assets/images/bowu/qtq/青铜器 青州博 清代 铜鎏金凤冠 服饰器.jpg", title: "青铜器 青州博 清代 铜鎏金凤冠 服饰器" },
        { src: "assets/images/bowu/qtq/青铜器 首都博 清代 铜魁星像 造像.jpg", title: "青铜器 首都博 清代 铜魁星像 造像" },
        { src: "assets/images/bowu/qtq/青铜器 首都博 西周 伯簋鼎 烹饪盛食器.jpg", title: "青铜器 首都博 西周 伯簋鼎 烹饪盛食器" },
        { src: "assets/images/bowu/qtq/青铜器 首都博 西周 早期乙公簋 盛食器.jpg", title: "青铜器 首都博 西周 早期乙公簋 盛食器" },
        { src: "assets/images/bowu/qtq/青铜器 首都博 西周 早期子方罍 盛酒器.jpg", title: "青铜器 首都博 西周 早期子方罍 盛酒器" },
        { src: "assets/images/bowu/qtq/青铜器 首都博 金代 铜坐龙 陈设器.jpg", title: "青铜器 首都博 金代 铜坐龙 陈设器" },
        { src: "assets/images/bowu/qtq/青铜器 齐文化 商代 亚醜钺 兵器.jpg", title: "青铜器 齐文化 商代 亚醜钺 兵器" },
        { src: "assets/images/bowu/qtq/青铜器 齐文化 战国 错红铜青铜龙纹壶 盛酒器.jpg", title: "青铜器 齐文化 战国 错红铜青铜龙纹壶 盛酒器" },
        { src: "assets/images/bowu/qtq/青铜器 齐文化 战国 错金银镶嵌铜牺尊 盛酒器.jpg", title: "青铜器 齐文化 战国 错金银镶嵌铜牺尊 盛酒器" },
        { src: "assets/images/bowu/qtq/青铜器 齐文化 战国 青铜提梁壶 盛酒器.jpg", title: "青铜器 齐文化 战国 青铜提梁壶 盛酒器" },
        { src: "assets/images/bowu/qtq/青铜器 齐文化 战国 龙形提梁青铜盉 调酒注水器.jpg", title: "青铜器 齐文化 战国 龙形提梁青铜盉 调酒注水器" },
        { src: "assets/images/bowu/qtq/青铜器 齐文化 春秋 龙耳铜簋 盛食器.jpg", title: "青铜器 齐文化 春秋 龙耳铜簋 盛食器" },
        { src: "assets/images/bowu/jyq/金银器 徐州博 商代 三星堆平顶青铜人头像吉金万里 金银器.jpg", title: "青铜器 徐州博 商代 三星堆平顶青铜人头像吉金万里" },
      { src: "assets/images/bowu/fjww/佛教文物 北京非遗工艺博 明代 明永乐款铜鎏金观音菩萨立像 供奉像.jpg", title: "佛教文物 北京非遗工艺博 明代 明永乐款铜鎏金观音菩萨立像 供奉像" },
        { src: "assets/images/bowu/fjww/佛教文物 四川省博 唐代 菩萨残立像 供奉像.jpg", title: "佛教文物 四川省博 唐代 菩萨残立像 供奉像" },
        { src: "assets/images/bowu/fjww/佛教文物 国博 元代 鎏金铜水月观音像 供奉像.jpg", title: "佛教文物 国博 元代 鎏金铜水月观音像 供奉像" },
        { src: "assets/images/bowu/fjww/佛教文物 国博 唐代 佛光寺东大殿模型 模型.jpg", title: "佛教文物 国博 唐代 佛光寺东大殿模型 模型" },
        { src: "assets/images/bowu/fjww/佛教文物 国博 唐代 南禅寺大殿模型 模型.jpg", title: "佛教文物 国博 唐代 南禅寺大殿模型 模型" },
        { src: "assets/images/bowu/fjww/佛教文物 国博 唐代 鎏金铜毗沙门天王像 护法像.jpg", title: "佛教文物 国博 唐代 鎏金铜毗沙门天王像 护法像" },
        { src: "assets/images/bowu/fjww/佛教文物 国博 宋代 彩绘木雕菩萨坐像 供奉像.jpg", title: "佛教文物 国博 宋代 彩绘木雕菩萨坐像 供奉像" },
        { src: "assets/images/bowu/fjww/佛教文物 国博 宋代 彩绘木雕观音菩萨坐像 供奉像.jpg", title: "佛教文物 国博 宋代 彩绘木雕观音菩萨坐像 供奉像" },
        { src: "assets/images/bowu/fjww/佛教文物 国博 宋代 彩绘木雕观音菩萨头像 供奉像.jpg", title: "佛教文物 国博 宋代 彩绘木雕观音菩萨头像 供奉像" },
        { src: "assets/images/bowu/fjww/佛教文物 国博 宋代 彩绘木雕观音菩萨立像 供奉像.jpg", title: "佛教文物 国博 宋代 彩绘木雕观音菩萨立像 供奉像" },
        { src: "assets/images/bowu/fjww/佛教文物 国博 宋代 紫竹观音 复制品.jpg", title: "佛教文物 国博 宋代 紫竹观音 复制品" },
        { src: "assets/images/bowu/fjww/佛教文物 国博 明代 三彩菩萨坐像 供奉像.jpg", title: "佛教文物 国博 明代 三彩菩萨坐像 供奉像" },
        { src: "assets/images/bowu/fjww/佛教文物 国博 明代 铜鎏金千手千眼观音菩萨像 供奉像.jpg", title: "佛教文物 国博 明代 铜鎏金千手千眼观音菩萨像 供奉像" },
        { src: "assets/images/bowu/fjww/佛教文物 国博 明代 铜鎏金观音菩萨立像 供奉像.jpg", title: "佛教文物 国博 明代 铜鎏金观音菩萨立像 供奉像" },
        { src: "assets/images/bowu/fjww/佛教文物 国博 辽代 应县木塔模型 模型.jpg", title: "佛教文物 国博 辽代 应县木塔模型 模型" },
        { src: "assets/images/bowu/fjww/佛教文物 国博 辽代 彩绘木雕水月观音坐像 供奉像.jpg", title: "佛教文物 国博 辽代 彩绘木雕水月观音坐像 供奉像" },
        { src: "assets/images/bowu/fjww/佛教文物 天津市博 明代 铜鎏金大持金刚像 护法像.jpg", title: "佛教文物 天津市博 明代 铜鎏金大持金刚像 护法像" },
        { src: "assets/images/bowu/fjww/佛教文物 湖北省博 明代 德化窑白釉观音坐像 供奉像.jpg", title: "佛教文物 湖北省博 明代 德化窑白釉观音坐像 供奉像" },
        { src: "assets/images/bowu/fjww/佛教文物 考古博 辽代 泥塑罗汉像 供奉像.jpg", title: "佛教文物 考古博 辽代 泥塑罗汉像 供奉像" },
        { src: "assets/images/bowu/fjww/佛教文物 青州博 南北朝 北齐贴金彩绘圆雕佛立像 供奉像.jpg", title: "佛教文物 青州博 南北朝 北齐贴金彩绘圆雕佛立像 供奉像" },
        { src: "assets/images/bowu/fjww/佛教文物 青州博 明代 德化窑白釉观音像 供奉像.jpg", title: "佛教文物 青州博 明代 德化窑白釉观音像 供奉像" },
        { src: "assets/images/bowu/fjww/佛教文物 首都博 元代 景德镇窑青白釉水月观音菩萨像 供奉像.jpg", title: "佛教文物 首都博 元代 景德镇窑青白釉水月观音菩萨像 供奉像" },
        { src: "assets/images/bowu/fjww/佛教文物 首都博 南北朝 北魏大代款铜鎏金释迦牟尼佛像 供奉像.jpg", title: "佛教文物 首都博 南北朝 北魏大代款铜鎏金释迦牟尼佛像 供奉像" },
        { src: "assets/images/bowu/fjww/佛教文物 首都博 南北朝 北魏太和廿三年阎惠端造释迦牟尼佛二胁侍菩萨像 供奉像.jpg", title: "佛教文物 首都博 南北朝 北魏太和廿三年阎惠端造释迦牟尼佛二胁侍菩萨像 供奉像" },
        { src: "assets/images/bowu/fjww/佛教文物 首都博 宋代 影青釉观音坐像 供奉像.jpg", title: "佛教文物 首都博 宋代 影青釉观音坐像 供奉像" },
        { src: "assets/images/bowu/fjww/佛教文物 首都博 明代 嘉靖款铜鎏金普贤菩萨像 供奉像.jpg", title: "佛教文物 首都博 明代 嘉靖款铜鎏金普贤菩萨像 供奉像" },
        { src: "assets/images/bowu/fjww/佛教文物 首都博 明代 织锦夹金五佛冠 法器.jpg", title: "佛教文物 首都博 明代 织锦夹金五佛冠 法器" },
        { src: "assets/images/bowu/fjww/佛教文物 首都博 明代 金嵌宝石梵文簪 法器.jpg", title: "佛教文物 首都博 明代 金嵌宝石梵文簪 法器" },
        { src: "assets/images/bowu/fjww/佛教文物 首都博 明代 铜增长天王像 护法像.jpg", title: "佛教文物 首都博 明代 铜增长天王像 护法像" },
        { src: "assets/images/bowu/fjww/佛教文物 首都博 清代 粉彩白度母瓷造像 供奉像.jpg", title: "佛教文物 首都博 清代 粉彩白度母瓷造像 供奉像" },
        { src: "assets/images/bowu/fjww/佛教文物 首都博 清代 金嵌宝石无量寿佛及金佛龛 供奉像.jpg", title: "佛教文物 首都博 清代 金嵌宝石无量寿佛及金佛龛 供奉像" },
        { src: "assets/images/bowu/fjww/佛教文物 首都博 清代 铜鎏金十字金刚杵 法器.jpg", title: "佛教文物 首都博 清代 铜鎏金十字金刚杵 法器" },
        { src: "assets/images/bowu/fjww/佛教文物 首都博 清代 铜鎏金绿度母像 供奉像.jpg", title: "佛教文物 首都博 清代 铜鎏金绿度母像 供奉像" },
        { src: "assets/images/bowu/fjww/佛教文物 首都博 清代 铜鎏金金刚铃头 法器.jpg", title: "佛教文物 首都博 清代 铜鎏金金刚铃头 法器" },
      { src: "assets/images/bowu/jyq/金银器 吉林省博 东汉 错金银丙午神钩铜带钩 鎏金器.jpg", title: "金银器 吉林省博 东汉 错金银丙午神钩铜带钩 鎏金器" },
        { src: "assets/images/bowu/jyq/金银器 吉林省博 汉代 夫余鎏金铜面具 供奉像.jpg", title: "金银器 吉林省博 汉代 夫余鎏金铜面具 供奉像" },
        { src: "assets/images/bowu/jyq/金银器 吉林省博 金代 金花玉饰腰带 金银器.jpg", title: "金银器 吉林省博 金代 金花玉饰腰带 金银器" },
        { src: "assets/images/bowu/jyq/金银器 国博 其他 隋炀帝萧皇后冠饰复原 饰件.jpg", title: "金银器 国博 其他 隋炀帝萧皇后冠饰复原 饰件" },
        { src: "assets/images/bowu/jyq/金银器 国博 唐代 立凤宝相花金饰件 饰件.jpg", title: "金银器 国博 唐代 立凤宝相花金饰件 饰件" },
        { src: "assets/images/bowu/jyq/金银器 国博 战国 错金银马首形青铜軏 鎏金器.jpg", title: "金银器 国博 战国 错金银马首形青铜軏 鎏金器" },
        { src: "assets/images/bowu/jyq/金银器 国博 战国 错银卧牛青铜镇 鎏金器.jpg", title: "金银器 国博 战国 错银卧牛青铜镇 鎏金器" },
        { src: "assets/images/bowu/jyq/金银器 国博 明代 闹蛾金钗 饰件.jpg", title: "金银器 国博 明代 闹蛾金钗 饰件" },
        { src: "assets/images/bowu/jyq/金银器 国博 西汉 滇王之印 印玺.jpg", title: "金银器 国博 西汉 滇王之印 印玺" },
        { src: "assets/images/bowu/jyq/金银器 国博 西汉 错金银云纹青铜犀尊 鎏金器.jpg", title: "金银器 国博 西汉 错金银云纹青铜犀尊 鎏金器" },
        { src: "assets/images/bowu/jyq/金银器 国博 西汉 错金银鸟篆文青铜壶 鎏金器.jpg", title: "金银器 国博 西汉 错金银鸟篆文青铜壶 鎏金器" },
        { src: "assets/images/bowu/jyq/金银器 徐州博 汉代 汉金带饰四件 金银器.jpg", title: "金银器 徐州博 汉代 汉金带饰四件 金银器" },
        { src: "assets/images/bowu/jyq/金银器 成都市博 唐代 花鸟纹金香囊 金银器.jpg", title: "金银器 成都市博 唐代 花鸟纹金香囊 金银器" },
        { src: "assets/images/bowu/jyq/金银器 湖北省博 明代 明金累丝镶宝石帽顶 金银器.jpg", title: "金银器 湖北省博 明代 明金累丝镶宝石帽顶 金银器" },
        { src: "assets/images/bowu/jyq/金银器 湖北省博 明代 明金镶宝石帽顶 金银器.jpg", title: "金银器 湖北省博 明代 明金镶宝石帽顶 金银器" },
        { src: "assets/images/bowu/jyq/金银器 辽宁省博 十六国 三燕花树状金步摇 金银器.jpg", title: "金银器 辽宁省博 十六国 三燕花树状金步摇 金银器" },
        { src: "assets/images/bowu/jyq/金银器 重庆三峡博 东汉 朔宁王太后玺 印玺.jpg", title: "金银器 重庆三峡博 东汉 朔宁王太后玺 印玺" },
        { src: "assets/images/bowu/jyq/金银器 重庆三峡博 战国 凤鸟纹错银铜壶 鎏金器.jpg", title: "金银器 重庆三峡博 战国 凤鸟纹错银铜壶 鎏金器" },
        { src: "assets/images/bowu/jyq/金银器 青州博 清代 铜鎏金凤冠 供奉像.jpg", title: "金银器 青州博 清代 铜鎏金凤冠 供奉像" },
        { src: "assets/images/bowu/jyq/金银器 首都博 明代 永乐款金凤簪 饰件.jpg", title: "金银器 首都博 明代 永乐款金凤簪 饰件" },
        { src: "assets/images/bowu/jyq/金银器 首都博 明代 累丝嵌珠石绵羊引子纹金簪 饰件.jpg", title: "金银器 首都博 明代 累丝嵌珠石绵羊引子纹金簪 饰件" },
        { src: "assets/images/bowu/jyq/金银器 首都博 明代 织锦夹金五佛冠 金银器.jpg", title: "金银器 首都博 明代 织锦夹金五佛冠 金银器" },
        { src: "assets/images/bowu/jyq/金银器 首都博 明代 金嵌宝石梵文簪 饰件.jpg", title: "金银器 首都博 明代 金嵌宝石梵文簪 饰件" },
        { src: "assets/images/bowu/jyq/金银器 首都博 明代 金累丝嵌宝石麒麟送子纹簪 饰件.jpg", title: "金银器 首都博 明代 金累丝嵌宝石麒麟送子纹簪 饰件" },
        { src: "assets/images/bowu/jyq/金银器 首都博 明代 金累丝嵌水晶螃蟹饰件 饰件.jpg", title: "金银器 首都博 明代 金累丝嵌水晶螃蟹饰件 饰件" },
        { src: "assets/images/bowu/jyq/金银器 首都博 明代 金镶宝石龙首带钩 金银器.jpg", title: "金银器 首都博 明代 金镶宝石龙首带钩 金银器" },
        { src: "assets/images/bowu/jyq/金银器 首都博 清代 累丝嵌宝石荷舟游人金饰件 饰件.jpg", title: "金银器 首都博 清代 累丝嵌宝石荷舟游人金饰件 饰件" },
        { src: "assets/images/bowu/jyq/金银器 首都博 清代 累丝嵌珠玉花蝶金簪 饰件.jpg", title: "金银器 首都博 清代 累丝嵌珠玉花蝶金簪 饰件" },
        { src: "assets/images/bowu/jyq/金银器 首都博 清代 累丝金龙舟饰件 饰件.jpg", title: "金银器 首都博 清代 累丝金龙舟饰件 饰件" },
        { src: "assets/images/bowu/jyq/金银器 首都博 清代 金嵌宝石无量寿佛及金佛龛 金银器.jpg", title: "金银器 首都博 清代 金嵌宝石无量寿佛及金佛龛 金银器" },
        { src: "assets/images/bowu/jyq/金银器 首都博 清代 铜胎鎏金掐丝珐琅三足熏炉 鎏金器.jpg", title: "金银器 首都博 清代 铜胎鎏金掐丝珐琅三足熏炉 鎏金器" },
        { src: "assets/images/bowu/jyq/金银器 首都博 清代 铜鎏金掐丝珐琅座钟 供奉像.jpg", title: "金银器 首都博 清代 铜鎏金掐丝珐琅座钟 供奉像" },
        { src: "assets/images/bowu/jyq/金银器 首都博 西晋 永嘉元年八子银铃 金银器.jpg", title: "金银器 首都博 西晋 永嘉元年八子银铃 金银器" },
        { src: "assets/images/bowu/jyq/金银器 首都博 金代 錾花寿桃纹金托盘 金银器.jpg", title: "金银器 首都博 金代 錾花寿桃纹金托盘 金银器" },
        { src: "assets/images/bowu/jyq/金银器 齐文化 战国 错金银镶嵌铜牺尊 鎏金器.jpg", title: "金银器 齐文化 战国 错金银镶嵌铜牺尊 鎏金器" },
       { src: "assets/images/bowu/tc/陶瓷 吉林省博 唐代 渤海三彩女俑 明器.jpg", title: "陶瓷 吉林省博 唐代 渤海三彩女俑 明器" },
      { src: "assets/images/bowu/tc/陶瓷 吉林省博 宋代 北宋官窑青釉贯耳瓶 盛贮器.jpg", title: "陶瓷 吉林省博 宋代 北宋官窑青釉贯耳瓶 盛贮器" },
        { src: "assets/images/bowu/tc/陶瓷 吉林省博 辽代 白釉贴花提梁壶 盛贮器.jpg", title: "陶瓷 吉林省博 辽代 白釉贴花提梁壶 盛贮器" },
        { src: "assets/images/bowu/tc/陶瓷 吉林省博 清代 清乾隆粉彩描金勾莲纹冠架 金银器.jpg", title: "陶瓷 吉林省博 清代 清乾隆粉彩描金勾莲纹冠架" },
        { src: "assets/images/bowu/tc/陶瓷 四川省博 东汉 乐舞百戏陶俑群 明器.jpg", title: "陶瓷 四川省博 东汉 乐舞百戏陶俑群 明器" },
        { src: "assets/images/bowu/tc/陶瓷 四川省博 东汉 陶说唱俑 明器.jpg", title: "陶瓷 四川省博 东汉 陶说唱俑 明器" },
        { src: "assets/images/bowu/tc/陶瓷 国博 东汉 击鼓说唱俑 明器.jpg", title: "陶瓷 国博 东汉 击鼓说唱俑 明器" },
        { src: "assets/images/bowu/tc/陶瓷 国博 东汉 绿釉陶楼 盛贮器.jpg", title: "陶瓷 国博 东汉 绿釉陶楼 盛贮器" },
        { src: "assets/images/bowu/tc/陶瓷 国博 南北朝 青瓷莲花尊 盛贮器.jpg", title: "陶瓷 国博 南北朝 青瓷莲花尊 盛贮器" },
        { src: "assets/images/bowu/tc/陶瓷 国博 唐代 三彩绞釉陶狩猎骑俑 明器.jpg", title: "陶瓷 国博 唐代 三彩绞釉陶狩猎骑俑 明器" },
        { src: "assets/images/bowu/tc/陶瓷 国博 唐代 三彩釉陶女俑 明器.jpg", title: "陶瓷 国博 唐代 三彩釉陶女俑 明器" },
        { src: "assets/images/bowu/tc/陶瓷 国博 唐代 三彩釉陶载乐骆驼 明器.jpg", title: "陶瓷 国博 唐代 三彩釉陶载乐骆驼 明器" },
        { src: "assets/images/bowu/tc/陶瓷 国博 唐代 三彩釉陶镇墓兽 明器.jpg", title: "陶瓷 国博 唐代 三彩釉陶镇墓兽 明器" },
        { src: "assets/images/bowu/tc/陶瓷 国博 唐代 彩绘釉陶武官俑、彩绘釉陶文吏俑 明器.jpg", title: "陶瓷 国博 唐代 彩绘釉陶武官俑、彩绘釉陶文吏俑 明器" },
        { src: "assets/images/bowu/tc/陶瓷 国博 唐代 白釉双龙耳瓶 盛贮器.jpg", title: "陶瓷 国博 唐代 白釉双龙耳瓶 盛贮器" },
        { src: "assets/images/bowu/tc/陶瓷 国博 新石器时代 舞蹈纹彩陶盆 盛贮器.jpg", title: "陶瓷 国博 新石器时代 舞蹈纹彩陶盆 盛贮器" },
        { src: "assets/images/bowu/tc/陶瓷 国博 新石器时代 陶鹰鼎 盛贮器.jpg", title: "陶瓷 国博 新石器时代 陶鹰鼎 盛贮器" },
        { src: "assets/images/bowu/tc/陶瓷 国博 清代 窑变釉甪端香薰 盛贮器.jpg", title: "陶瓷 国博 清代 窑变釉甪端香薰 盛贮器" },
        { src: "assets/images/bowu/tc/陶瓷 国博 清代 粉彩镂空转心瓶 陶瓷.jpg", title: "陶瓷 国博 清代 粉彩镂空转心瓶 陶瓷" },
        { src: "assets/images/bowu/tc/陶瓷 国博 辽代 绿釉鸱吻 建筑构件.jpg", title: "陶瓷 国博 辽代 绿釉鸱吻 建筑构件" },
        { src: "assets/images/bowu/tc/陶瓷 天津市博 清代 清乾隆款珐琅彩芍药雉鸡纹玉壶春瓶 陶瓷.jpg", title: "陶瓷 天津市博 清代 清乾隆款珐琅彩芍药雉鸡纹玉壶春瓶 陶瓷" },
        { src: "assets/images/bowu/tc/陶瓷 天津市博 清代 翡翠缠枝菊花纹环耳扁盖瓶 陶瓷.jpg", title: "陶瓷 天津市博 清代 翡翠缠枝菊花纹环耳扁盖瓶 陶瓷" },
        { src: "assets/images/bowu/tc/陶瓷 天津市博 隋代 白釉双龙柄联腹传瓶 盛贮器.jpg", title: "陶瓷 天津市博 隋代 白釉双龙柄联腹传瓶 盛贮器" },
        { src: "assets/images/bowu/tc/陶瓷 徐州博 南北朝 北朝彩绘陶双髻执笏女立俑 明器.jpg", title: "陶瓷 徐州博 南北朝 北朝彩绘陶双髻执笏女立俑 明器" },
        { src: "assets/images/bowu/tc/陶瓷 成都市博 东汉 击鼓说唱俑 明器.jpg", title: "陶瓷 成都市博 东汉 击鼓说唱俑 明器" },
        { src: "assets/images/bowu/tc/陶瓷 成都市博 五代 后蜀彩绘陶花冠女舞俑 明器.jpg", title: "陶瓷 成都市博 五代 后蜀彩绘陶花冠女舞俑 明器" },
        { src: "assets/images/bowu/tc/陶瓷 考古博 元代 青白釉梅花纹双耳瓷瓶 盛贮器.jpg", title: "陶瓷 考古博 元代 青白釉梅花纹双耳瓷瓶 盛贮器" },
        { src: "assets/images/bowu/tc/陶瓷 考古博 唐代 唐绿彩联腹龙柄传瓶 陶瓷.jpg", title: "陶瓷 考古博 唐代 唐绿彩联腹龙柄传瓶 陶瓷" },
        { src: "assets/images/bowu/tc/陶瓷 考古博 唐代 渤海国釉陶鸱尾 建筑构件.jpg", title: "陶瓷 考古博 唐代 渤海国釉陶鸱尾 建筑构件" },
        { src: "assets/images/bowu/tc/陶瓷 考古博 新石器时代 人像彩陶罐 盛贮器.jpg", title: "陶瓷 考古博 新石器时代 人像彩陶罐 盛贮器" },
        { src: "assets/images/bowu/tc/陶瓷 考古博 新石器时代 立鸟异形陶器 盛贮器.jpg", title: "陶瓷 考古博 新石器时代 立鸟异形陶器 盛贮器" },
        { src: "assets/images/bowu/tc/陶瓷 考古博 明代 彩绘釉陶仪仗俑群 明器.jpg", title: "陶瓷 考古博 明代 彩绘釉陶仪仗俑群 明器" },
        { src: "assets/images/bowu/tc/陶瓷 辽宁省博 清代 清光绪粉彩荷花吸杯粉彩缠枝莲纹碗粉彩堆贴螭龙纹瓶 陶瓷.jpg", title: "陶瓷 辽宁省博 清代 清光绪粉彩荷花吸杯粉彩缠枝莲纹碗粉彩堆贴螭龙纹瓶 陶瓷" },
        { src: "assets/images/bowu/tc/陶瓷 辽宁省博 清代 清雍正窑变釉石榴尊 盛贮器.jpg", title: "陶瓷 辽宁省博 清代 清雍正窑变釉石榴尊 盛贮器" },
        { src: "assets/images/bowu/tc/陶瓷 辽宁省博 清代 粉彩花卉纹玉壶春瓶 陶瓷.jpg", title: "陶瓷 辽宁省博 清代 粉彩花卉纹玉壶春瓶 陶瓷" },
        { src: "assets/images/bowu/tc/陶瓷 辽宁省博 辽代 辽青瓷飞鱼形水盂 盛贮器.jpg", title: "陶瓷 辽宁省博 辽代 辽青瓷飞鱼形水盂 盛贮器" },
        { src: "assets/images/bowu/tc/陶瓷 青州博 明代 孔雀蓝釉双龙瓶 盛贮器.jpg", title: "陶瓷 青州博 明代 孔雀蓝釉双龙瓶 盛贮器" },
        { src: "assets/images/bowu/tc/陶瓷 青州博 清代 清道光白釉褐彩蛙形花盆 盛贮器.jpg", title: "陶瓷 青州博 清代 清道光白釉褐彩蛙形花盆 盛贮器" },
      { src: "assets/images/bowu/yq/玉器 吉林省博 金代 玉带銙 服饰器.jpg", title: "玉器 吉林省博 金代 玉带銙 服饰器" },
        { src: "assets/images/bowu/yq/玉器 吉林省博 金代 白玉耳杯 玉器.jpg", title: "玉器 吉林省博 金代 白玉耳杯 玉器" },
        { src: "assets/images/bowu/yq/玉器 四川省博 五代 前蜀龙纹玉大带 服饰器.jpg", title: "玉器 四川省博 五代 前蜀龙纹玉大带 服饰器" },
        { src: "assets/images/bowu/yq/玉器 四川省博 新石器时代 大溪文化人面形玉佩 陈设器.jpg", title: "玉器 四川省博 新石器时代 大溪文化人面形玉佩 陈设器" },
        { src: "assets/images/bowu/yq/玉器 国博 新石器时代 新石器红山文化玉龙 陈设器.jpg", title: "玉器 国博 新石器时代 新石器红山文化玉龙 陈设器" },
        { src: "assets/images/bowu/yq/玉器 国博 新石器时代 玦形龙 佩饰.jpg", title: "玉器 国博 新石器时代 玦形龙 佩饰" },
        { src: "assets/images/bowu/yq/玉器 国博 新石器时代 玦形龙玉猪龙 佩饰.jpg", title: "玉器 国博 新石器时代 玦形龙玉猪龙 佩饰" },
        { src: "assets/images/bowu/yq/玉器 国博 新石器时代 红山文化玉猪龙 玉器.jpg", title: "玉器 国博 新石器时代 红山文化玉猪龙 玉器" },
        { src: "assets/images/bowu/yq/玉器 国博 新石器时代 良渚文化十九节玉琮 礼器.jpg", title: "玉器 国博 新石器时代 良渚文化十九节玉琮 礼器" },
        { src: "assets/images/bowu/yq/玉器 国博 清代 银鎏金点翠镶玉嵌玛瑙饰件 佩饰.jpg", title: "玉器 国博 清代 银鎏金点翠镶玉嵌玛瑙饰件 佩饰" },
        { src: "assets/images/bowu/yq/玉器 国博 西汉 金缕玉衣.jpg", title: "玉器 国博 西汉 金缕玉衣" },
        { src: "assets/images/bowu/yq/玉器 天津市博 东汉 青玉双螭谷纹玉璧 礼器.jpg", title: "玉器 天津市博 东汉 青玉双螭谷纹玉璧 礼器" },
        { src: "assets/images/bowu/yq/玉器 天津市博 新石器时代 红山文化黄玉猪龙 玉器.jpg", title: "玉器 天津市博 新石器时代 红山文化黄玉猪龙 玉器" },
        { src: "assets/images/bowu/yq/玉器 天津市博 清代 翡翠缠枝菊花纹环耳扁盖瓶 佩饰.jpg", title: "玉器 天津市博 清代 翡翠缠枝菊花纹环耳扁盖瓶 佩饰" },
        { src: "assets/images/bowu/yq/玉器 徐州博 西汉 出廓透雕螭虎玉戈 仪仗器.jpg", title: "玉器 徐州博 西汉 出廓透雕螭虎玉戈 仪仗器" },
        { src: "assets/images/bowu/yq/玉器 徐州博 西汉 出廓龙纹玉璜 礼器.jpg", title: "玉器 徐州博 西汉 出廓龙纹玉璜 礼器" },
        { src: "assets/images/bowu/yq/玉器 徐州博 西汉 出廓龙纹玉璜抠图 礼器.jpg", title: "玉器 徐州博 西汉 出廓龙纹玉璜抠图 礼器" },
        { src: "assets/images/bowu/yq/玉器 徐州博 西汉 玉卮 玉器.jpg", title: "玉器 徐州博 西汉 玉卮 玉器" },
        { src: "assets/images/bowu/yq/玉器 徐州博 西汉 透雕龙凤纹玉环 佩饰.jpg", title: "玉器 徐州博 西汉 透雕龙凤纹玉环 佩饰" },
        { src: "assets/images/bowu/yq/玉器 徐州博 西汉 金缕玉衣.jpg", title: "玉器 徐州博 西汉 金缕玉衣" },
        { src: "assets/images/bowu/yq/玉器 徐州博 西汉 银缕玉衣.jpg", title: "玉器 徐州博 西汉 银缕玉衣" },
        { src: "assets/images/bowu/yq/玉器 徐州博 西汉 食官监漆木芯镶玉枕 玉器.jpg", title: "玉器 徐州博 西汉 食官监漆木芯镶玉枕 玉器" },
        { src: "assets/images/bowu/yq/玉器 徐州博 西汉 龙形玉佩 佩饰.jpg", title: "玉器 徐州博 西汉 龙形玉佩 佩饰" },
        { src: "assets/images/bowu/yq/玉器 考古博 商代 玉鸮 陈设器.jpg", title: "玉器 考古博 商代 玉鸮 陈设器" },
        { src: "assets/images/bowu/yq/玉器 辽宁省博 新石器时代 红山文化玉猪龙 玉器.jpg", title: "玉器 辽宁省博 新石器时代 红山文化玉猪龙 玉器" },
        { src: "assets/images/bowu/yq/玉器 重庆三峡博 东汉 朔宁王太后玺 印玺.jpg", title: "玉器 重庆三峡博 东汉 朔宁王太后玺 印玺" },
        { src: "assets/images/bowu/yq/玉器 青州博 东汉 宜子孙玉璧 礼器.jpg", title: "玉器 青州博 东汉 宜子孙玉璧 礼器" }
      ]

    },
     {
      city: "中国 北京",
      desc: "",
      seal: "京",
      star: true,          //  星标：封面左上角会出现一枚圆形铜钱标
      tags: ["颐和园", "北海", "雍和宫", "天安门", "天坛", "中山公园"],
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
        { src: "assets/images/travel-44.jpg", title: "北海之夏" },
        { src: "assets/images/bj2/bj201.jpg", title: "雍和宫其二" },
        { src: "assets/images/bj2/bj202.jpg", title: "雍和宫其三" },
        { src: "assets/images/bj2/bj203.jpg", title: "雍和宫其四" },  
        { src: "assets/images/bj2/bj204.jpg", title: "国子监小胡同" },
        { src: "assets/images/bj2/bj205.jpg", title: "地坛公园" },
        { src: "assets/images/bj2/bj206.jpg", title: "北京智化寺" },
        { src: "assets/images/bj2/bj207.jpg", title: "北京站" },
        { src: "assets/images/bj2/bj208.jpg", title: "中山公园 西雁翅楼" },
        { src: "assets/images/bj2/bj209.jpg", title: "中山城景" },
        { src: "assets/images/bj2/bj210.jpg", title: "圣弥厄尔天主堂 东交民巷" },
        { src: "assets/images/bj2/bj211.jpg", title: "颐和园 万寿山" },
        { src: "assets/images/bj2/bj212.jpg", title: "颐和园 万寿山其二" },
        { src: "assets/images/bj2/bj213.jpg", title: "颐和园 益寿堂" },
        { src: "assets/images/bj2/bj214.jpg", title: "颐和园 谐趣园其二" },
        { src: "assets/images/bj2/bj215.jpg", title: "颐和园 仁寿殿" },
        { src: "assets/images/bj2/bj216.jpg", title: "昆明湖景" },
        { src: "assets/images/bj2/bj217.jpg", title: "昆明湖景 其二" },
        { src: "assets/images/bj2/bj218.jpg", title: "颐和园 文昌阁" },
        { src: "assets/images/bj2/bj219.jpg", title: "颐和园 廊桥" },
        { src: "assets/images/bj2/bj220.jpg", title: "颐和园 排云殿" },
        { src: "assets/images/bj2/bj221.jpg", title: "颐和园 佛香阁 其二" },
        { src: "assets/images/bj2/bj222.jpg", title: "颐和园 谐趣园 其三" },
        { src: "assets/images/bj2/bj223.jpg", title: "天坛项背" },
        { src: "assets/images/bj2/bj224.jpg", title: "天坛中轴" },
        { src: "assets/images/bj2/bj225.jpg", title: "天坛远眺" },
        { src: "assets/images/bj2/bj226.jpg", title: "天坛辉光" },
        { src: "assets/images/bj2/bj227.jpg", title: "零碎日落" },
        { src: "assets/images/bj2/bj228.jpg", title: "天坛 圜丘坛" },
        { src: "assets/images/bj2/bj229.jpg", title: "鼓楼大街" },
        { src: "assets/images/bj2/bj230.jpg", title: "什刹海 日间" },
        { src: "assets/images/bj2/bj231.jpg", title: "北海之夏 其二" },
        { src: "assets/images/bj2/bj232.jpg", title: "北海之夏 其三" },
        { src: "assets/images/bj2/bj233.jpg", title: "北海之夏 其四" },
        { src: "assets/images/bj2/bj234.jpg", title: "北海之夏 其五" },
        { src: "assets/images/bj2/bj235.jpg", title: "万佛殿秋英丛" },
        { src: "assets/images/bj2/bj237.jpg", title: "北海之夏 其六" },
        { src: "assets/images/bj2/bj238.jpg", title: "北海之夏 其七" },
        { src: "assets/images/bj2/bj239.jpg", title: "北海之夏 其八" },
        { src: "assets/images/bj2/bj236.jpg", title: "太庙一隅" },
        { src: "assets/images/bj2/tiananmen/天安门.jpg", title: "天安门" },
        { src: "assets/images/bj2/tiananmen/天安门 其二.jpg", title: "天安门 其二" },
        { src: "assets/images/bj2/tiananmen/天安门 其三.jpg", title: "天安门 其三" }
      ]
    },
        {
      city: "北京 圆明园遗址公园",
      desc: "",
      seal: "圆明园",
      star: true, 
      tags: ["大水法", "海晏堂", "鸿慈永秙", "遗址", "鸳鸯", "荷"],
      photos: [
        { src: "assets/images/bj2/ymy/圆明园西洋楼景区的大水法遗址3.jpg", title: "大水法遗址 " },
        { src: "assets/images/bj2/ymy/圆明园西洋楼景区的大水法遗址2.jpg", title: "大水法遗址 其二" },
        { src: "assets/images/bj2/ymy/远瀛观遗址.jpg", title: "远瀛观遗址" },
        { src: "assets/images/bj2/ymy/海晏堂遗址1.jpg", title: "海晏堂遗址" },
        { src: "assets/images/bj2/ymy/海晏堂遗址3.jpg", title: "海晏堂遗址 其二" },
        { src: "assets/images/bj2/ymy/海晏堂遗址4.jpg", title: "海晏堂遗址 其三" },
        { src: "assets/images/bj2/ymy/方外观.jpg", title: "方外观" },
        { src: "assets/images/bj2/ymy/五竹亭遗址.jpg", title: "五竹亭遗址" },
        { src: "assets/images/bj2/ymy/观水法遗址1.jpg", title: "观水法遗址" },
        { src: "assets/images/bj2/ymy/谐奇趣遗迹.jpg", title: "谐奇趣遗址" },
        { src: "assets/images/bj2/ymy/黄花阵2.jpg", title: "黄花阵" },
        { src: "assets/images/bj2/ymy/黄花阵3.jpg", title: "黄花阵 其二" },
        { src: "assets/images/bj2/ymy/圆明园 正觉寺后门.jpg", title: "正觉寺后门" },
        { src: "assets/images/bj2/ymy/圆明园 绮春园2.jpg", title: "绮春园" },
        { src: "assets/images/bj2/ymy/圆明园 绮春园5.jpg", title: "绮春园 其二" },
        { src: "assets/images/bj2/ymy/圆明园 长春园.jpg", title: "圆明园 长春园" },
        { src: "assets/images/bj2/ymy/圆明园 长春园2.jpg", title: "圆明园 长春园 其二" },
        { src: "assets/images/bj2/ymy/圆明园 长春园4.jpg", title: "圆明园 长春园 其三" },
        { src: "assets/images/bj2/ymy/圆明园之荷.jpg", title: "圆明园之荷" },
        { src: "assets/images/bj2/ymy/圆明园之荷2.jpg", title: "圆明园之荷 其二" },
        { src: "assets/images/bj2/ymy/圆明园之莲2.jpg", title: "圆明园之莲" },
        { src: "assets/images/bj2/ymy/圆明园之莲3.jpg", title: "圆明园之莲 其二" },
        { src: "assets/images/bj2/ymy/圆明园博物馆.jpg", title: "圆明园博物馆" },
        { src: "assets/images/bj2/ymy/圆明园白骨顶鸡2.jpg", title: "圆明园白骨顶鸡" },
        { src: "assets/images/bj2/ymy/圆明园花丛16.jpg", title: "圆明园花丛" },
        { src: "assets/images/bj2/ymy/圆明园花丛20.jpg", title: "圆明园花丛 其二" },
        { src: "assets/images/bj2/ymy/圆明园花丛6.jpg", title: "圆明园花丛 其三" },
        { src: "assets/images/bj2/ymy/圆明园鸭子1.jpg", title: "圆明园鸭子" },
        { src: "assets/images/bj2/ymy/圆明园鸭子与锦鲤2.jpg", title: "圆明园鸭子与锦鲤" },
        { src: "assets/images/bj2/ymy/圆明园鸳鸯.jpg", title: "圆明园鸳鸯" },
        { src: "assets/images/bj2/ymy/圆明园鸳鸯2.jpg", title: "圆明园鸳鸯 其二" },
        { src: "assets/images/bj2/ymy/圆明园鸳鸯4.jpg", title: "圆明园鸳鸯 其三" },
        { src: "assets/images/bj2/ymy/圆明园鸳鸯5.jpg", title: "圆明园鸳鸯 其四" },
        { src: "assets/images/bj2/ymy/圆明园黑天鹅.jpg", title: "圆明园黑天鹅" },
        { src: "assets/images/bj2/ymy/藻园小玳瑁.jpg", title: "藻园 小玳瑁" },
        { src: "assets/images/bj2/ymy/藻园鸽子2.jpg", title: "藻园 鸽子" },
        { src: "assets/images/bj2/ymy/鸿慈永秙 锦鲤2.jpg", title: "鸿慈永秙 锦鲤" },
        { src: "assets/images/bj2/ymy/鸿慈永秙11.jpg", title: "鸿慈永秙" },
        { src: "assets/images/bj2/ymy/鸿慈永秙12.jpg", title: "鸿慈永秙 其二" },
        { src: "assets/images/bj2/ymy/鸿慈永秙13.jpg", title: "鸿慈永秙 其三" },
        { src: "assets/images/bj2/ymy/鸿慈永秙15.jpg", title: "鸿慈永秙 其四" },
        { src: "assets/images/bj2/ymy/鸿慈永秙18.jpg", title: "鸿慈永秙 其五" },
        { src: "assets/images/bj2/ymy/鸿慈永秙4.jpg", title: "鸿慈永秙 其六" },
        { src: "assets/images/bj2/ymy/鸿慈永秙7.jpg", title: "鸿慈永秙 其七" },
        { src: "assets/images/bj2/ymy/鸿慈永秙9.jpg", title: "鸿慈永秙 其八" },
      ]
    },
        {
      city: "古建筑构建盘点",
      desc: "",
      seal: "构件",
      star: true,
      tags: ["脊兽"],
      photos: [
        { src: "assets/images/bj3/骑凤仙人.jpg", title: "脊兽第一 骑凤仙人" },
        { src: "assets/images/bj3/龙.jpg", title: "脊兽第二 龙" },
        { src: "assets/images/bj3/凤.jpg", title: "脊兽第三 凤" },
        { src: "assets/images/bj3/狮子.jpg", title: "脊兽第四 狮子" },
        { src: "assets/images/bj3/海马.jpg", title: "脊兽第五 海马" },
        { src: "assets/images/bj3/天马.jpg", title: "脊兽第六 天马" },
        { src: "assets/images/bj3/狎鱼.jpg", title: "脊兽第七 狎鱼" },
        { src: "assets/images/bj3/狻猊.jpg", title: "脊兽第八 狻猊" },
        { src: "assets/images/bj3/獬豸.jpg", title: "脊兽第九 獬豸" },
        { src: "assets/images/bj3/斗牛.jpg", title: "脊兽第十 斗牛" },
        { src: "assets/images/bj3/行什.jpg", title: "脊兽十一 行什" }
      ]
    },
        {
      city: "北京 九坛八庙",
      desc: "",
      seal: "坛庙",
      star: true, 
      tags: ["天坛", "太庙", "社稷坛", "地坛", "先蚕坛"],
      photos: [ 
        { src: "assets/images/bj3/jtbm/天坛 祈年殿.jpg", title: "天坛 祈年殿" },
        { src: "assets/images/bj3/jtbm/天坛 回音壁.jpg", title: "天坛 回音壁" },
        { src: "assets/images/bj3/jtbm/天坛 圜丘坛.jpg", title: "天坛 圜丘坛" },
        { src: "assets/images/bj3/jtbm/先蚕坛.jpg", title: "先蚕坛" },
        { src: "assets/images/bj3/jtbm/地坛.jpg", title: "地坛" },
        { src: "assets/images/bj3/jtbm/太岁殿大殿.jpg", title: "太岁殿大殿" },
        { src: "assets/images/bj3/jtbm/拜殿.jpg", title: "拜殿" },
        { src: "assets/images/bj3/jtbm/神仓.jpg", title: "神仓" },
        { src: "assets/images/bj3/jtbm/太庙.jpg", title: "太庙" },
        { src: "assets/images/bj3/jtbm/太庙  其二.jpg", title: "太庙  其二" },
        { src: "assets/images/bj3/jtbm/景山 寿皇殿.jpg", title: "景山 寿皇殿" },
        { src: "assets/images/bj3/jtbm/社稷坛.jpg", title: "社稷坛" },
        { src: "assets/images/bj3/jtbm/社稷坛 其二.jpg", title: "社稷坛 其二" }
      ]
    },
    {
      city: "中国 重庆",
      desc: "",
      seal: "渝",          // 本图集专属印章字（不想要就删掉这一行，会统一用 site.photoSeal）
      star: true,          // ← 星标：封面左上角会出现一枚圆形铜钱标记（不想要就删掉这行）
      tags: ["老君洞", "华岩寺", "风吹岭", "夜", "江"],
      photos: [
        { src: "assets/images/travel-16.jpg", title: "嘉陵江意" },
        { src: "assets/images/travel-17.jpg", title: "长江国际" },
        { src: "assets/images/travel-18.jpg", title: "南岸夜潮" },
        { src: "assets/images/travel-19.jpg", title: "川美后街" },
        { src: "assets/images/cq2/cq201.jpg", title: "解放碑广场" },
        { src: "assets/images/cq2/cq216.jpg", title: "母城夜景" },
        { src: "assets/images/cq2/cq202.jpg", title: "得意世界之夜" },
        { src: "assets/images/cq2/cq203.jpg", title: "老君洞" },
        { src: "assets/images/cq2/cq204.jpg", title: "老君洞其二" },
        { src: "assets/images/cq2/cq206.jpg", title: "老君洞其三" },
        { src: "assets/images/cq2/cq205.jpg", title: "雾都缆车" },
        { src: "assets/images/cq2/cq207.jpg", title: "风吹岭马尿水瀑布" },
        { src: "assets/images/travel-21.jpg", title: "风吹岭云海" },
        { src: "assets/images/travel-20.jpg", title: "南川风吹岭登山处" },
        { src: "assets/images/cq2/cq208.jpg", title: "风吹岭山顶" },
        { src: "assets/images/cq2/cq209.jpg", title: "桥流之构" },
        { src: "assets/images/cq2/cq210.jpg", title: "华岩寺" },
        { src: "assets/images/cq2/cq211.jpg", title: "华岩寺其二" },
        { src: "assets/images/cq2/cq212.jpg", title: "山城步道南纪门轨道大桥" },
        { src: "assets/images/cq2/cq213.jpg", title: "军哥书店" },
        { src: "assets/images/cq2/cq214.jpg", title: "南岸老街区" },
        { src: "assets/images/cq2/cq215.jpg", title: "南岸机车" },
        { src: "assets/images/cq2/cq217.jpg", title: "龙泉观" },
        { src: "assets/images/cq2/cq218.jpg", title: "铁西四村" },
        { src: "assets/images/cq2/cq219.jpg", title: "大剧院与大江" }
      ]
    },
      {
      city: "吉林 长春",
      desc: "",
      seal: "长",
      star: true, 
      tags: ["净月潭", "红旗街", "同志街", "电车"],
      photos: [
        { src: "assets/images/changchun20260916018.jpg", title: "漫画轻轨" },
        { src: "assets/images/changchun20260916004.jpg", title: "长春大学之春" },
        { src: "assets/images/changchun20260916001.jpg", title: "卫星广场午后" },
        { src: "assets/images/changchun20260916002.jpg", title: "友谊公园" },
        { src: "assets/images/changchun20260916005.jpg", title: "文化广场" },
        { src: "assets/images/changchun20260916006.jpg", title: "净月潭" },
        { src: "assets/images/changchun20260916007.jpg", title: "净月潭其二" },
        { src: "assets/images/changchun20260916008.jpg", title: "净月潭其三" },
        { src: "assets/images/changchun20260916009.jpg", title: "净月潭其四" },
        { src: "assets/images/changchun20260916012.jpg", title: "净月潭其五" },
        { src: "assets/images/travel-8.jpg", title: "净月潭其六" },
        { src: "assets/images/changchun20260916003.jpg", title: "同志街十字路口" },
        { src: "assets/images/changchun20260916010.jpg", title: "同志街其二" },
        { src: "assets/images/changchun20260916011.jpg", title: "长大之夜" },
        { src: "assets/images/changchun20260916013.jpg", title: "红旗街电车" },
        { src: "assets/images/changchun20260916017.jpg", title: "红旗街电车其二" },
        { src: "assets/images/changchun20260916014.jpg", title: "夜中三号线" },
        { src: "assets/images/changchun20260916015.jpg", title: "雪中长春站北站" },
        { src: "assets/images/changchun20260916016.jpg", title: "长春文庙" },
        { src: "assets/images/changchun20260916019.jpg", title: "54路电车" }
      ]
    },
     {
      city: "长春伪满和建国初期建筑",
      desc: "",
      seal: "伪满",
      star: true,  
      tags: ["伪满皇宫", "伪满", "建国", "东本愿寺", "鸣放宫"],
      photos: [
        { src: "assets/images/weiman1.jpg", title: "东本愿寺" },
        { src: "assets/images/weiman2.jpg", title: "伪满中央银行旧址" },
        { src: "assets/images/weiman3.jpg", title: "伪满交通部旧址" },
        { src: "assets/images/weiman4.jpg", title: "伪满关东军司令部旧址" },
        { src: "assets/images/weiman5.jpg", title: "伪满兴农部旧址" },
        { src: "assets/images/weiman6.jpg", title: "伪满民生部旧址" },
        { src: "assets/images/weiman7.jpg", title: "伪满皇宫 勤民楼" },
        { src: "assets/images/weiman8.jpg", title: "伪满皇宫 勤民楼二" },
        { src: "assets/images/weiman9.jpg", title: "伪满皇宫 勤民楼勤民殿一" },
        { src: "assets/images/weiman10.jpg", title: "伪满皇宫 勤民楼勤民殿二" },
        { src: "assets/images/weiman11.jpg", title: "伪满皇宫 同德殿" },
        { src: "assets/images/weiman12.jpg", title: "伪满皇宫 同德殿2" },
        { src: "assets/images/weiman13.jpg", title: "伪满皇宫 同德殿3" },
        { src: "assets/images/weiman14.jpg", title: "伪满皇宫兴运门" },
        { src: "assets/images/weiman15.jpg", title: "伪满皇宫同德殿 御学问所" },
        { src: "assets/images/weiman16.jpg", title: "伪满皇宫缉熙楼" },
        { src: "assets/images/weiman17.jpg", title: "伪满皇宫缉熙楼二" },
        { src: "assets/images/weiman18.jpg", title: "伪满皇宫花园" },
        { src: "assets/images/weiman19.jpg", title: "伪满综合法衙旧址" },
        { src: "assets/images/weiman20.jpg", title: "吉林大学基础医学院（伪满司法部旧址）" },
        { src: "assets/images/weiman21.jpg", title: "吉林大学新民校区教学楼（伪满国务院旧址）" },
        { src: "assets/images/weiman22.jpg", title: "吉林大学白求恩医学部（伪满司法部旧址）" },
        { src: "assets/images/weiman23.jpg", title: "吉林大学白求恩第一医院（伪满军事部旧址）" },
        { src: "assets/images/weiman24.jpg", title: "吉林大学第三医院（伪满经济部旧址）" },
        { src: "assets/images/weiman25.jpg", title: "吉长道尹公署旧址" },
        { src: "assets/images/weiman26.jpg", title: "地质宫" },
        { src: "assets/images/weiman27.jpg", title: "建国鬼子庙" },
        { src: "assets/images/weiman28.jpg", title: "建国鬼子庙二" },
        { src: "assets/images/weiman29.jpg", title: "长春站" },
        { src: "assets/images/weiman30.jpg", title: "鸣放宫" },
        { src: "assets/images/weiman31.jpg", title: "鸣放宫二" },
        { src: "assets/images/weiman32.jpg", title: "鸣放宫摩天轮同框" }
      ]
    },
    {
      city: "山东 淄博",
      desc: "",
      seal: "淄", 
      tags: ["四宝山", "桓台", "周村", "淄川", "海岱楼"],
      photos: [
        { src: "assets/images/travel-13.jpg", title: "四宝山俯拍" },
        { src: "assets/images/travel-14.jpg", title: "叹淄景" },
        { src: "assets/images/zb2/zb201.jpg", title: "桓台除夕夜" },
        { src: "assets/images/zb2/zb202.jpg", title: "桓台马踏湖" },
        { src: "assets/images/zb2/zb203.jpg", title: "齐盛湖 其二" },
        { src: "assets/images/zb2/zb204.jpg", title: "四宝山" },
        { src: "assets/images/zb2/zb205.jpg", title: "淄川 蒲松龄故居" },
        { src: "assets/images/zb2/zb206.jpg", title: "桓台扫街" },
        { src: "assets/images/zb2/zb207.jpg", title: "淄博交通银行" },
        { src: "assets/images/zb2/zb208.jpg", title: "中国课本博物馆" },
        { src: "assets/images/zb2/zb209.jpg", title: "桓台四世宫保牌坊" },
        { src: "assets/images/zb2/zb210.jpg", title: "桓台王渔洋故居" },
        { src: "assets/images/zb2/zb211.jpg", title: "周村旱码头牌坊" },
        { src: "assets/images/zb2/zb212.jpg", title: "周村武状元府" },
        { src: "assets/images/zb2/zb213.jpg", title: "周村古城春和榭" },
        { src: "assets/images/zb2/zb214.jpg", title: "周村古城观海楼" },
        { src: "assets/images/zb2/zb215.jpg", title: "周村古城观海楼 其二" },
        { src: "assets/images/zb2/zb216.jpg", title: "四宝山俯拍 其二" },
        { src: "assets/images/zb2/zb217.jpg", title: "淄博高新文体公园" },
        { src: "assets/images/zb2/zb218.jpg", title: "四宝山俯拍 其三" },
        { src: "assets/images/zb2/zb219.jpg", title: "海岱楼" },
        { src: "assets/images/zb2/八大局.jpg", title: "八大局" },
        { src: "assets/images/zb2/唐库.jpg", title: "唐库文创园" }
      ]
    },
    {
      city: "辽宁 沈阳",
      desc: "",
      seal: "沈",
      star: true,  
      tags: ["清故宫", "北陵公园", "中街", "工业博物馆", "教堂", "扫街"],
      photos: [
        { src: "assets/images/travel-4.jpg", title: "北陵公园" },
        { src: "assets/images/sy2/sy201.jpg", title: "沈阳小南教堂" },
        { src: "assets/images/sy2/sy202.jpg", title: "东北大学" },
        { src: "assets/images/sy2/sy203.jpg", title: "北陵公园" },
        { src: "assets/images/sy2/sy204.jpg", title: "沈阳之夜" },
        { src: "assets/images/sy2/sy205.jpg", title: "清故宫藻井" },
        { src: "assets/images/sy2/sy206.jpg", title: "沈阳站" },
        { src: "assets/images/sy2/sy207.jpg", title: "西塔" },
        { src: "assets/images/sy2/sy208.jpg", title: "中山广场一" },
        { src: "assets/images/sy2/sy209.jpg", title: "中山广场二" },
        { src: "assets/images/sy2/sy210.jpg", title: "中山广场三" },
        { src: "assets/images/sy2/sy211.jpg", title: "西塔二扫街" },
        { src: "assets/images/sy2/sy212.jpg", title: "清故宫皇座" },
        { src: "assets/images/sy2/sy213.jpg", title: "大政殿" },
        { src: "assets/images/sy2/sy214.jpg", title: "清故宫二" },
        { src: "assets/images/sy2/sy215.jpg", title: "清故宫三" },
        { src: "assets/images/sy2/sy216.jpg", title: "东三省总督府" },
        { src: "assets/images/sy2/sy217.jpg", title: "清故宫四" },
        { src: "assets/images/sy2/sy218.jpg", title: "九一八纪念馆" },
        { src: "assets/images/sy2/sy219.jpg", title: "大帅府一" },
        { src: "assets/images/sy2/sy220.jpg", title: "小青楼" },
        { src: "assets/images/sy2/sy221.jpg", title: "沈阳中街" },
        { src: "assets/images/sy2/sy222.jpg", title: "清故宫五" },
        { src: "assets/images/sy2/sy223.jpg", title: "张学良雕像" },
        { src: "assets/images/sy2/sy224.jpg", title: "沈阳中街二" },
        { src: "assets/images/sy2/sy225.jpg", title: "沈阳故宫文化博物馆" },
        { src: "assets/images/sy2/sy226.jpg", title: "沈阳扫街" },
        { src: "assets/images/sy2/sy227.jpg", title: "清故宫六" },
        { src: "assets/images/sy2/sy228.jpg", title: "北陵公园二" },
        { src: "assets/images/sy2/sy229.jpg", title: "沈阳扫街二" },
        { src: "assets/images/sy2/sy230.jpg", title: "工业母城" },
        { src: "assets/images/sy2/sy231.jpg", title: "中国工业博物馆" },
        { src: "assets/images/sy2/sy232.jpg", title: "中国工业博物馆二" },
        { src: "assets/images/sy2/sy233.jpg", title: "中国工业博物馆三" },
        { src: "assets/images/sy2/sy234.jpg", title: "北陵公园三" },
        { src: "assets/images/sy2/sy235.jpg", title: "北陵公园四" },
        { src: "assets/images/sy2/sy236.jpg", title: "华表" },
        { src: "assets/images/sy2/sy237.jpg", title: "北陵公园五" },
        { src: "assets/images/sy2/sy238.jpg", title: "沈阳故宫文德坊" },
        { src: "assets/images/sy2/sy239.jpg", title: "清故宫七" },
        { src: "assets/images/sy2/sy240.jpg", title: "清故宫八" },
        { src: "assets/images/sy2/sy241.jpg", title: "北陵公园三" }
      ]
    },
     {
      city: "辽宁 大连",
      desc: "",
      seal: "连",
      star: true,  
      tags: ["星海广场", "莲花山", "渔人码头", "东港", "威尼斯"],
      photos: [
        { src: "assets/images/travel-9.jpg", title: "星海广场" },
        { src: "assets/images/dl2/dl12.jpg", title: "星海广场大桥其二" },
        { src: "assets/images/dl2/dl13.jpg", title: "星海广场大桥其三" },
        { src: "assets/images/dl2/dl10.jpg", title: "大连中山广场" },
        { src: "assets/images/travel-26.jpg", title: "莲花山顶" },
        { src: "assets/images/dl2/dl03.jpg", title: "莲花山俯瞰大桥" },
        { src: "assets/images/dl2/大连美术馆.jpg", title: "大连美术馆" },
        { src: "assets/images/travel-27.jpg", title: "渔人码头" },
        { src: "assets/images/dl2/dl01.jpg", title: "渔人码头其二" },
        { src: "assets/images/dl2/dl02.jpg", title: "渔人码头其三" },
        { src: "assets/images/dl2/dl04.jpg", title: "东港" },
        { src: "assets/images/dl2/dl05.jpg", title: "东港其二" },
        { src: "assets/images/dl2/dl06.jpg", title: "东港其三" },
        { src: "assets/images/dl2/dl07.jpg", title: "仿威尼斯水城" },
        { src: "assets/images/dl2/dl11.jpg", title: "仿威尼斯水城其二" }, 
        { src: "assets/images/dl2/dl09.jpg", title: "联兴巷" },
        { src: "assets/images/dl2/dl14.jpg", title: "黑石礁" }
      ]
    },
       {
      city: "华东四市",
      seal: "沪苏杭",
      desc: "2019初至",
      tags: ["上海", "杭州", "乌镇", "苏州"],
      photos: [    
        { src: "assets/images/hdws/上海外滩 夜.jpg", title: "上海外滩 夜" },
        { src: "assets/images/hdws/上海外滩 日.jpg", title: "上海外滩 日" },
        { src: "assets/images/hdws/上海人民广场 地铁站.jpg", title: "上海人民广场 地铁站" },
        { src: "assets/images/hdws/杭州 西湖 .jpg", title: "杭州 西湖 " },
        { src: "assets/images/hdws/杭州 西湖 其二.jpg", title: "杭州 西湖 其二" },
        { src: "assets/images/hdws/浙江嘉兴桐乡 乌镇东栅.jpg", title: "浙江嘉兴桐乡 乌镇东栅" },
        { src: "assets/images/hdws/浙江嘉兴桐乡 乌镇西栅.jpg", title: "浙江嘉兴桐乡 乌镇西栅" },
        { src: "assets/images/hdws/苏州 耦园.jpg", title: "苏州 耦园" },
        { src: "assets/images/hdws/苏州 山塘街.jpg", title: "苏州 山塘街" },
        { src: "assets/images/hdws/苏州山塘街 其二.jpg", title: "苏州 山塘街 其二" }
      ]
    },
    {
      city: "江苏 徐州",
      desc: "",
      seal: "彭",
      photos: [
        { src: "assets/images/travel-5.jpg", title: "户部山" }
      ]
    },
        {
      city: "陕西 西安",
      desc: "2021年高考结束 至渭南、西安游玩。",
      seal: "秦",
      tags: ["华山", "兵马俑", "不夜城", "骊山", "华清池"],
      photos: [
        { src: "assets/images/xian/2021年 大唐不夜城.jpg", title: "2021年 大唐不夜城" },
        { src: "assets/images/xian/华山盛景.jpg", title: "华山盛景" },
        { src: "assets/images/xian/华山盛景 其二.jpg", title: "华山盛景 其二" },
        { src: "assets/images/xian/华山盛景 其三.jpg", title: "华山盛景 其三" },
        { src: "assets/images/xian/华山盛景 其四.jpg", title: "华山盛景 其四" },
        { src: "assets/images/xian/华山盛景 其五.jpg", title: "华山盛景 其五" },
        { src: "assets/images/xian/华山盛景 其六.jpg", title: "华山盛景 其六" },
        { src: "assets/images/xian/华山盛景 其七.jpg", title: "华山盛景 其七" },    
        { src: "assets/images/xian/华山盛景 其八.jpg", title: "华山盛景 其八" },
        { src: "assets/images/xian/华山盛景 其九.jpg", title: "华山盛景 其九" },
        { src: "assets/images/xian/秦始皇陵兵马俑.jpg", title: "秦始皇陵兵马俑" },
        { src: "assets/images/xian/秦始皇陵兵马俑 其二.jpg", title: "秦始皇陵兵马俑 其二" },
        { src: "assets/images/xian/秦始皇陵兵马俑 其三.jpg", title: "秦始皇陵兵马俑 其三" },
        { src: "assets/images/xian/骊山索道.jpg", title: "骊山索道" },
        { src: "assets/images/xian/华清池景区 老蒋谏兵亭.jpg", title: "华清池景区 老蒋谏兵亭" },
      ]
    },
    {
      city: "山东 泰安",
      desc: "",
      seal: "泰",
      tags: ["泰山"],
      photos: [
        { src: "assets/images/travel-6.jpg", title: "泰山 南天门" }
      ]
    },
    {
      city: "山东 青州",
      desc: "",
      seal: "青",
      photos: [
        { src: "assets/images/travel-7.jpg", title: "青州古城落日" }
      ]
    },
  
    {
      city: "湖北 武汉",
      desc: "",
      seal: "汉",
      photos: [
        { src: "assets/images/travel-10.jpg", title: "黄鹤楼之夜" }
      ]
    },
    {
      city: "中国 天津",
      desc: "",
      seal: "津",
      photos: [
        { src: "assets/images/travel-11.jpg", title: "津湾广场" }
      ]
    },
    {
      city: "江苏 连云港",
      desc: "",
      seal: "海",
      photos: [
        { src: "assets/images/travel-12.jpg", title: "在海一方公园" }
      ]
    },
    {
      city: "四川 成都",
      desc: "",
      seal: "蓉",
      photos: [
        { src: "assets/images/travel-15.jpg", title: "天府广场" },
        { src: "assets/images/travel-25.jpg", title: "青羊宫" }
      ]
    },
    {
      city: "黑龙江 哈尔滨",
      desc: "",
      seal: "哈",
      photos: [
        { src: "assets/images/travel-22.jpg", title: "中央大街" }
      ]
    },
    {
      city: "山东 济南",
      desc: "",
      seal: "济",
      photos: [
        { src: "assets/images/travel-23.jpg", title: "曲水亭街" },
        { src: "assets/images/travel-24.jpg", title: "胶济铁路博物馆" }
      ]
    },
       {
      city: "名胜古迹 三山五岳",
      desc: "2021年至西岳华山，2025年至东岳泰山，2026年至北岳恒山。",
      seal: "五岳",
      star: true,  
      tags: ["泰山", "华山"],
      photos: [
        { src: "assets/images/wuyue/东岳 泰山.jpg", title: "东岳 泰山" },
        { src: "assets/images/wuyue/西岳 华山.jpg", title: "西岳 华山" }

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
         "西安"    系统自动识别为「陕西」并点亮陕西省
         "济南"    自动识别为「山东」
         系统内置「城市→省份」对照表（约 150 个主要城市）。

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
    "徐州", "连云港", "成都", "重庆", "武汉", 
    "大同","西安@陕西","渭南@陕西" ,"上海","苏州","杭州",
    "无锡","郑州","唐山","青岛@山东","广州@广东"],

  /* ─────────── 叁 · 所好（个人爱好） ───────────
     icon 可选值：brush(毛笔) camera(相机) tea(茶) mountain(登山)
     book(书) guqin(琴) chess(棋) lower(花) music(乐) run(跑) */
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
