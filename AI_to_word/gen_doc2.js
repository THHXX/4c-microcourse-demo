/**
 * 生成：中国大学生计算机设计大赛 AI工具使用说明（2026年版）
 * 作品：卷积核微课——AI助教驱动的卷积神经网络可视化虚拟实验室
 */
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  AlignmentType, BorderStyle, WidthType, ShadingType, VerticalAlign
} = require('C:/Users/JYJYJ/AppData/Roaming/npm/node_modules/docx');
const fs = require('fs');

// ─── 样式 ──────────────────────────────────────────────────────────────────
const headerFill = 'D9E1F2';
const subHeaderFill = 'EBF0FA';
const border = { style: BorderStyle.SINGLE, size: 4, color: '4472C4' };
const thinBorder = { style: BorderStyle.SINGLE, size: 2, color: '9DC3E6' };
const thinBorders = { top: thinBorder, bottom: thinBorder, left: thinBorder, right: thinBorder };

function cell(text, opts = {}) {
  const {
    bold = false, fill = null, colSpan = 1, align = 'left', size = 19,
    italic = false, color = '000000', vertAlign = VerticalAlign.CENTER
  } = opts;
  const parts = text.split('\n');
  const runs = [];
  parts.forEach((p, i) => {
    if (i > 0) runs.push(new TextRun({ break: 1 }));
    runs.push(new TextRun({ text: p, bold, size, font: '仿宋', color, italics: italic }));
  });
  return new TableCell({
    columnSpan: colSpan,
    borders: thinBorders,
    shading: fill ? { fill, type: ShadingType.CLEAR } : undefined,
    verticalAlign: vertAlign,
    margins: { top: 60, bottom: 60, left: 100, right: 100 },
    children: [new Paragraph({
      alignment: align === 'center' ? AlignmentType.CENTER
               : align === 'right'  ? AlignmentType.RIGHT : AlignmentType.LEFT,
      children: runs,
      spacing: { before: 40, after: 40 }
    })]
  });
}

function hCell(text, colSpan = 1) {
  return cell(text, { bold: true, fill: headerFill, colSpan, align: 'center', size: 19 });
}
function lCell(text, colSpan = 1) {
  return cell(text, { bold: true, fill: subHeaderFill, colSpan, align: 'center', size: 19 });
}
function dCell(text, colSpan = 1, align = 'left') {
  return cell(text, { colSpan, align, size: 18 });
}

// ─── 页面尺寸 ──────────────────────────────────────────────────────────────
const PAGE_W  = 11906;
const MARGIN  = 720;
const CONTENT = PAGE_W - MARGIN * 2;  // 10466

// ─── AI使用记录行 ─────────────────────────────────────────────────────────
const AI_RECORDS = [
  {
    no: '1',
    tool: 'Claude Code（claude-sonnet-4-6），Anthropic，\n客户端+API方式，\n2026年3月15日—4月15日',
    purpose: '代码编程、功能架构设计、调试优化：\n使用Claude Code辅助设计FastAPI后端框架、前后端一体化页面、流式SSE对话接口、笔记持久化、视频截图、Word/HTML导出功能全链路代码',
    prompt: '"基于FastAPI构建微课学习平台，需要：①视频播放 ②流式AI对话（SSE） ③笔记/截图功能 ④跨页面导出Word/PDF，使用通义千问qwen-plus API，前后端一体，Python f-string内嵌JS需双重转义"',
    reply: '提供了完整的FastAPI+前端一体化框架（约7000行）；实现SSE流式响应；生成了前端UI组件、Canvas动画、导出Modal、localStorage持久化等核心功能代码（详见附录截图AI-01~AI-08）',
    modify: '重新设计了UI配色（暖橙色系）和动画效果；优化Canvas卷积核滑动算法；补充了错误处理；将Python f-string内的JS代码中${}和反斜杠进行双重转义修复，共人工修改约3500行',
    ratio: 'AI生成核心框架约65%\n经人工重构后最终采纳约45%'
  },
  {
    no: '2',
    tool: '通义千问（qwen-plus），\n阿里云DashScope，\nAPI方式，\n2026年3月20日起持续集成',
    purpose: '作为AI助教功能组件直接集成到作品中：\n为学习者提供卷积核、特征图、激活函数、池化层等计算机视觉知识点的实时流式问答服务，是作品核心教学功能之一',
    prompt: '（系统提示词）"你是专业的计算机视觉与深度学习助教，专注于卷积神经网络教学。用通俗易懂的语言解释卷积核、特征图、池化、激活函数等概念，结合作品中的可视化动画给出具体示例，鼓励学习者自主探索。"',
    reply: '对学习者提问的卷积核尺寸选择、特征图维度计算、填充（Padding）策略、步幅（Stride）效果等知识点给出了清晰的教学解释，并能结合动画交互上下文给出个性化引导（详见附录AI-09）',
    modify: '无需人工修改（作为教学功能API直接调用，输出内容即时展示给学习者）',
    ratio: '100%（作为功能组件集成，所有输出均直接呈现）'
  },
  {
    no: '3',
    tool: 'Claude AI（claude.ai），\nAnthropic，网页方式，\n2026年3月10日—3月25日',
    purpose: '立项构思、教学内容设计、作品简介及创新描述撰写：\n辅助确定微课知识点组织顺序，建议教学模块划分，润色文字表述',
    prompt: '"为大学生设计卷积核微课，目标受众是计算机视觉初学者，需覆盖：卷积运算原理、卷积核类型（边缘检测/模糊/锐化）、特征提取过程、与全连接层的关系，建议合理的教学顺序和重难点分配"',
    reply: '建议了"三步法"教学结构（理论讲解→动画演示→AI辅助实践），提出知识点组织框架：①卷积基本概念→②卷积核类型与效果→③可视化演示→④AI问答强化（详见附录AI-10）',
    modify: '根据实际教学经验调整了知识点顺序，增加了可交互Canvas动画演示模块，删减了过于理论化的部分，自行撰写了所有正式的文字内容',
    ratio: '框架思路采纳约70%，具体文字内容100%自行撰写'
  }
];

const aiRows = AI_RECORDS.map(r => new TableRow({ children: [
  dCell(r.no, 1, 'center'),
  dCell(r.tool),
  dCell(r.purpose),
  dCell(r.prompt),
  dCell(r.reply),
  dCell(r.modify),
  dCell(r.ratio, 1, 'center')
]}));

// 列宽：序号 | 工具 | 环节目的 | 提示词 | 回复内容 | 人工修改 | 采纳比例
const COL_WIDTHS = [500, 1600, 2000, 2100, 1700, 1400, 1166];

const doc = new Document({
  styles: {
    default: { document: { run: { font: '仿宋', size: 19 } } },
    paragraphStyles: [
      {
        id: 'title', name: 'Title',
        run: { font: '黑体', size: 32, bold: true, color: '17375E' },
        paragraph: { alignment: AlignmentType.CENTER, spacing: { before: 200, after: 100 } }
      }
    ]
  },
  sections: [{
    properties: {
      page: {
        size: { width: PAGE_W, height: 16838 },
        margin: { top: MARGIN, right: MARGIN, bottom: MARGIN, left: MARGIN }
      }
    },
    children: [

      // ── 标题 ──────────────────────────────────────────────────────────────
      new Paragraph({
        style: 'title',
        children: [new TextRun({ text: '中国大学生计算机设计大赛', font: '黑体', size: 32, bold: true, color: '17375E' })]
      }),
      new Paragraph({
        style: 'title',
        children: [new TextRun({ text: 'AI工具使用说明', font: '黑体', size: 36, bold: true, color: '17375E' })]
      }),
      new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { before: 80, after: 200 },
        children: [new TextRun({ text: '（2026年版）', font: '仿宋', size: 22, color: '4472C4' })]
      }),

      // ── 基本信息 ──────────────────────────────────────────────────────────
      new Table({
        width: { size: CONTENT, type: WidthType.DXA },
        columnWidths: [2000, 3233, 2000, 3233],
        rows: [
          new TableRow({ children: [
            lCell('作品编号'),
            dCell('（系统分配）'),
            lCell('作品名称'),
            dCell('卷积核微课——AI助教驱动的卷积神经网络可视化虚拟实验室')
          ]})
        ]
      }),

      new Paragraph({ children: [], spacing: { before: 120 } }),

      // ── AI使用说明表 ───────────────────────────────────────────────────────
      new Table({
        width: { size: CONTENT, type: WidthType.DXA },
        columnWidths: COL_WIDTHS,
        rows: [
          // 表头
          new TableRow({ children: [
            hCell('序号'),
            hCell('AI工具名称、版本、访问方式、使用时间'),
            hCell('使用AI工具的环节与目的'),
            hCell('关键提示词'),
            hCell('AI回复的关键内容'),
            hCell('AI回复的人工修改说明'),
            hCell('采纳比例与说明')
          ]}),
          // 数据行
          ...aiRows
        ]
      }),

      new Paragraph({ children: [], spacing: { before: 120 } }),

      // ── 填写说明 ──────────────────────────────────────────────────────────
      new Table({
        width: { size: CONTENT, type: WidthType.DXA },
        columnWidths: [CONTENT],
        rows: [
          new TableRow({ children: [
            new TableCell({
              borders: thinBorders,
              shading: { fill: 'FFF2CC', type: ShadingType.CLEAR },
              margins: { top: 100, bottom: 100, left: 150, right: 150 },
              children: [
                new Paragraph({
                  children: [new TextRun({ text: '填写说明：', bold: true, font: '仿宋', size: 19 })]
                }),
                new Paragraph({
                  children: [new TextRun({
                    text: '1. 本文档如实记录了本作品在开发过程中使用AI工具的全部情况，包括Claude Code（代码开发）、通义千问（AI助教集成）、Claude AI（内容构思）三类工具。',
                    font: '仿宋', size: 18
                  })]
                }),
                new Paragraph({
                  children: [new TextRun({
                    text: '2. AI回复关键内容的佐证截图详见本文档附录（截图含时间戳，文件命名：AI_使用序号_作品编号.png）。',
                    font: '仿宋', size: 18
                  })]
                }),
                new Paragraph({
                  children: [new TextRun({
                    text: '3. 代码中的AI辅助生成部分已在注释中标注，格式：# AI辅助生成：claude-sonnet-4-6, 2026-03-XX。',
                    font: '仿宋', size: 18
                  })]
                }),
                new Paragraph({
                  children: [new TextRun({
                    text: '4. 本文档内容真实填写，如有不属实情况，自愿承担相应责任。',
                    font: '仿宋', size: 18
                  })]
                }),
                new Paragraph({ children: [], spacing: { before: 100 } }),
                new Paragraph({
                  children: [new TextRun({ text: '全体作者签名：唐浩涵　　李梦琪　　陈思远', font: '仿宋', size: 19 })]
                }),
                new Paragraph({
                  children: [new TextRun({ text: '日期：2026年 4 月 16 日', font: '仿宋', size: 19 })]
                }),
              ]
            })
          ]})
        ]
      }),
    ]
  }]
});

Packer.toBuffer(doc).then(buf => {
  fs.writeFileSync('F:/Desktop/个人资料/学校作业/大三下学期作业/计算机设计大赛/卷积核微课/框架/2-AI工具使用说明（已填写）.docx', buf);
  console.log('✅ AI工具使用说明 生成完毕');
}).catch(e => { console.error(e); process.exit(1); });
