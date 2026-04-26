/**
 * 生成：中国大学生计算机设计大赛 作品信息概要表（2026年版）
 * 作品：卷积核微课——AI助教驱动的卷积神经网络可视化虚拟实验室
 */
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  AlignmentType, BorderStyle, WidthType, ShadingType, VerticalAlign,
  HeadingLevel, UnderlineType
} = require('C:/Users/JYJYJ/AppData/Roaming/npm/node_modules/docx');
const fs = require('fs');

// ─── 颜色 & 边框 ───────────────────────────────────────────────────────────
const headerFill = 'D9E1F2';
const subHeaderFill = 'EBF0FA';
const border = { style: BorderStyle.SINGLE, size: 4, color: '4472C4' };
const borders = { top: border, bottom: border, left: border, right: border };
const thinBorder = { style: BorderStyle.SINGLE, size: 2, color: '9DC3E6' };
const thinBorders = { top: thinBorder, bottom: thinBorder, left: thinBorder, right: thinBorder };

// ─── 辅助函数 ──────────────────────────────────────────────────────────────
function cell(text, opts = {}) {
  const {
    bold = false, fill = null, colSpan = 1, align = 'left', size = 19,
    italic = false, color = '000000', wrap = true, vertAlign = VerticalAlign.CENTER
  } = opts;
  const runs = [];
  const parts = text.split('\n');
  parts.forEach((p, idx) => {
    if (idx > 0) runs.push(new TextRun({ break: 1 }));
    runs.push(new TextRun({
      text: p, bold, size, font: '仿宋', color, italics: italic
    }));
  });
  return new TableCell({
    columnSpan: colSpan,
    borders: thinBorders,
    shading: fill ? { fill, type: ShadingType.CLEAR } : undefined,
    verticalAlign: vertAlign,
    margins: { top: 60, bottom: 60, left: 100, right: 100 },
    children: [new Paragraph({
      alignment: align === 'center' ? AlignmentType.CENTER :
                 align === 'right'  ? AlignmentType.RIGHT : AlignmentType.LEFT,
      children: runs,
      spacing: { before: 40, after: 40 }
    })]
  });
}

function headerCell(text, colSpan = 1) {
  return cell(text, { bold: true, fill: headerFill, colSpan, align: 'center', size: 20 });
}

function labelCell(text, colSpan = 1) {
  return cell(text, { bold: true, fill: subHeaderFill, colSpan, align: 'center', size: 19 });
}

function dataCell(text, colSpan = 1, align = 'left') {
  return cell(text, { colSpan, align, size: 19 });
}

function pct(v) { return v ? `${v}%` : ''; }

// ─── 文档 ──────────────────────────────────────────────────────────────────
const PAGE_W = 11906;   // A4 宽 (DXA)
const MARGIN  = 720;    // 页边距 0.5 英寸
const CONTENT = PAGE_W - MARGIN * 2; // 10466 DXA

const doc = new Document({
  styles: {
    default: {
      document: { run: { font: '仿宋', size: 19 } }
    },
    paragraphStyles: [
      {
        id: 'title', name: 'Title',
        run: { font: '黑体', size: 32, bold: true, color: '17375E' },
        paragraph: { alignment: AlignmentType.CENTER, spacing: { before: 200, after: 100 } }
      },
      {
        id: 'subtitle', name: 'Subtitle',
        run: { font: '仿宋', size: 22, color: '2E5F8E' },
        paragraph: { alignment: AlignmentType.CENTER, spacing: { before: 80, after: 240 } }
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
        children: [new TextRun({ text: '作品信息概要表', font: '黑体', size: 36, bold: true, color: '17375E' })]
      }),
      new Paragraph({
        style: 'subtitle',
        children: [new TextRun({ text: '（2026年版）', font: '仿宋', size: 22, color: '4472C4' })]
      }),

      // ── 主信息表 ─────────────────────────────────────────────────────────
      new Table({
        width: { size: CONTENT, type: WidthType.DXA },
        columnWidths: [2000, 2000, 2000, 4466],
        rows: [
          // 作品编号 / 作品名称
          new TableRow({ children: [
            labelCell('作品编号', 1),
            dataCell('（系统分配）', 1),
            labelCell('作品名称', 1),
            dataCell('卷积核微课——AI助教驱动的卷积神经网络可视化虚拟实验室', 1)
          ]}),
          // 作品大类 / 小类
          new TableRow({ children: [
            labelCell('作品大类', 1),
            dataCell('微课与人工智能辅助教学类', 1),
            labelCell('作品小类', 1),
            dataCell('虚拟仿真实验', 1)
          ]}),
          // 参赛学校
          new TableRow({ children: [
            labelCell('参赛学校', 1),
            dataCell('华南师范大学', 1),
            labelCell('学院/系', 1),
            dataCell('计算机学院', 1)
          ]}),
        ]
      }),

      new Paragraph({ children: [], spacing: { before: 80 } }),

      // ── 作品简介 ──────────────────────────────────────────────────────────
      new Table({
        width: { size: CONTENT, type: WidthType.DXA },
        columnWidths: [2000, 8466],
        rows: [
          new TableRow({ children: [
            labelCell('作品简介\n（100字以内）'),
            dataCell(
              '本作品构建了基于Web技术的卷积核可视化微课虚拟实验室，融合微课视频教学、交互式Canvas动画演示与通义千问AI助教三大模块，实现"观看—理解—问答"一体化自主学习闭环，帮助学生直观理解卷积神经网络工作机制，有效降低深度学习入门门槛。'
            )
          ]}),
          new TableRow({ children: [
            labelCell('创新描述\n（100字以内）'),
            dataCell(
              '首创"微课视频+Canvas实时动画+AI助教"三位一体教学架构；Canvas动画可实时演示卷积核滑动与特征图生成过程，化抽象数学运算为可感知视觉体验；嵌入通义千问大模型提供个性化即时答疑；FastAPI后端+纯前端技术栈，浏览器即开即用，零门槛部署。'
            )
          ]})
        ]
      }),

      new Paragraph({ children: [], spacing: { before: 80 } }),

      // ── 特别说明 ──────────────────────────────────────────────────────────
      new Table({
        width: { size: CONTENT, type: WidthType.DXA },
        columnWidths: [2000, 8466],
        rows: [
          new TableRow({ children: [
            labelCell('特别说明'),
            dataCell(
              '1. 本作品不涉及地图内容，无需标注审图号。\n' +
              '2. 本作品为本次大赛全新原创，无前期公开发表基础。本次参赛主要工作：从零设计教学框架、开发Web虚拟实验室系统、录制微课视频、集成通义千问AI助教、制作课后交互式学习资料全套。\n' +
              '3. 本作品在架构设计与代码开发过程中使用了Claude Code（claude-sonnet-4-6）及通义千问API等AI辅助工具，详见"2-AI工具使用说明（2026年版）"。'
            )
          ]})
        ]
      }),

      new Paragraph({ children: [], spacing: { before: 80 } }),

      // ── 作者分工 ──────────────────────────────────────────────────────────
      new Table({
        width: { size: CONTENT, type: WidthType.DXA },
        columnWidths: [2100, 2788, 2788, 2790],
        rows: [
          new TableRow({ children: [
            new TableCell({
              columnSpan: 4, borders: thinBorders,
              shading: { fill: headerFill, type: ShadingType.CLEAR },
              margins: { top: 60, bottom: 60, left: 100, right: 100 },
              children: [new Paragraph({
                alignment: AlignmentType.CENTER,
                children: [new TextRun({ text: '作者及其分工比例', bold: true, font: '仿宋', size: 20 })]
              })]
            })
          ]}),
          new TableRow({ children: [
            headerCell('项目名称'),
            headerCell('唐浩涵（组长）'),
            headerCell('李梦琪'),
            headerCell('陈思远')
          ]}),
          new TableRow({ children: [labelCell('组织协调'), dataCell('60%', 1, 'center'), dataCell('25%', 1, 'center'), dataCell('15%', 1, 'center')] }),
          new TableRow({ children: [labelCell('作品创意'), dataCell('40%', 1, 'center'), dataCell('35%', 1, 'center'), dataCell('25%', 1, 'center')] }),
          new TableRow({ children: [labelCell('竞品分析'), dataCell('30%', 1, 'center'), dataCell('40%', 1, 'center'), dataCell('30%', 1, 'center')] }),
          new TableRow({ children: [labelCell('方案设计'), dataCell('50%', 1, 'center'), dataCell('30%', 1, 'center'), dataCell('20%', 1, 'center')] }),
          new TableRow({ children: [labelCell('技术实现'), dataCell('65%', 1, 'center'), dataCell('20%', 1, 'center'), dataCell('15%', 1, 'center')] }),
          new TableRow({ children: [labelCell('文献阅读'), dataCell('25%', 1, 'center'), dataCell('40%', 1, 'center'), dataCell('35%', 1, 'center')] }),
          new TableRow({ children: [labelCell('测试分析'), dataCell('40%', 1, 'center'), dataCell('30%', 1, 'center'), dataCell('30%', 1, 'center')] }),
        ]
      }),

      new Paragraph({ children: [], spacing: { before: 80 } }),

      // ── 指导教师 & 平台 ───────────────────────────────────────────────────
      new Table({
        width: { size: CONTENT, type: WidthType.DXA },
        columnWidths: [2000, 8466],
        rows: [
          new TableRow({ children: [
            labelCell('指导教师\n（姓名、职称）'),
            dataCell('王志刚，副教授，华南师范大学计算机学院')
          ]}),
          new TableRow({ children: [
            labelCell('指导教师作用'),
            dataCell('☑作品创意  ☑理论指导  ☑技术方案  □实验场地  □硬件资源\n□数据提供  □后勤支持  ☑宣讲通知  □组织协调  □经费支持')
          ]}),
          new TableRow({ children: [
            labelCell('开发制作平台'),
            dataCell('☑Windows  □Linux  □macOS  □其他')
          ]}),
          new TableRow({ children: [
            labelCell('运行展示平台'),
            dataCell('☑Windows  ☑Linux  ☑macOS  □iOS  □Android  □其他（浏览器跨平台运行）')
          ]}),
          new TableRow({ children: [
            labelCell('开发制作工具'),
            dataCell('Python 3.11 / FastAPI 0.110 / Uvicorn / 通义千问API (qwen-plus) / Claude Code / VS Code / Node.js / HTML5 Canvas / JavaScript ES6+')
          ]})
        ]
      }),

      new Paragraph({ children: [], spacing: { before: 80 } }),

      // ── 参考文献 ──────────────────────────────────────────────────────────
      new Table({
        width: { size: CONTENT, type: WidthType.DXA },
        columnWidths: [2000, 8466],
        rows: [
          new TableRow({ children: [
            labelCell('参考文献\n（前3项）'),
            dataCell(
              '1. LeCun Y, Bengio Y, Hinton G. Deep learning[J]. Nature, 2015, 521(7553): 436-444.\n' +
              '2. 邱锡鹏. 神经网络与深度学习[M]. 机械工业出版社, 2020.\n' +
              '3. FastAPI官方文档. https://fastapi.tiangolo.com/'
            )
          ]})
        ]
      }),

      new Paragraph({ children: [], spacing: { before: 80 } }),

      // ── 提交内容 ──────────────────────────────────────────────────────────
      new Table({
        width: { size: CONTENT, type: WidthType.DXA },
        columnWidths: [2000, 8466],
        rows: [
          new TableRow({ children: [
            labelCell('提交内容'),
            dataCell('☑素材压缩包  ☑设计文档  ☑演示视频  ☑PPT  ☑源代码  □部署文件  □数据集  □模型  ☑作品文件  □其他')
          ]})
        ]
      }),

      new Paragraph({ children: [], spacing: { before: 80 } }),

      // ── 相关文件 ──────────────────────────────────────────────────────────
      new Table({
        width: { size: CONTENT, type: WidthType.DXA },
        columnWidths: [500, 2800, 3883, 2283],
        rows: [
          new TableRow({ children: [
            new TableCell({
              columnSpan: 4, borders: thinBorders,
              shading: { fill: headerFill, type: ShadingType.CLEAR },
              margins: { top: 60, bottom: 60, left: 100, right: 100 },
              children: [new Paragraph({
                alignment: AlignmentType.CENTER,
                children: [new TextRun({ text: '相关文件', bold: true, font: '仿宋', size: 20 })]
              })]
            })
          ]}),
          new TableRow({ children: [
            headerCell('序号'), headerCell('文件名与描述'), headerCell('文件状态'), headerCell('版权状态')
          ]}),
          ...[
            ['1', '文件名：作品信息概要表.pdf\n描述：本参赛作品信息概要，必填模板', '☑已上传到网盘\n□未上传', '☑自制\n□开源□获得授权'],
            ['2', '文件名：AI工具使用说明.pdf\n描述：AI工具使用情况详细说明', '☑已上传到网盘\n□未上传', '☑自制\n□开源□获得授权'],
            ['3', '文件名：卷积核微课演示视频.mp4\n描述：作品完整运行演示视频（约5分钟）', '☑已上传到网盘\n□未上传', '☑自制\n□开源□获得授权'],
            ['4', '文件名：项目源代码.zip\n描述：FastAPI后端+前端全部源代码', '☑已上传到网盘\n□未上传', '☑自制\n□开源□获得授权'],
            ['5', '文件名：课后学习资料.html\n描述：交互式课后学习资料（含可视化动画）', '☑已上传到网盘\n□未上传', '☑自制\n□开源□获得授权'],
            ['6', '文件名：答辩演示PPT.pdf\n描述：现场答辩使用的演示文稿PDF版', '☑已上传到网盘\n□未上传', '☑自制\n□开源□获得授权'],
          ].map(([no, desc, status, copy]) => new TableRow({ children: [
            dataCell(no, 1, 'center'),
            dataCell(desc),
            dataCell(status),
            dataCell(copy)
          ]}))
        ]
      }),

      new Paragraph({ children: [], spacing: { before: 120 } }),

      // ── 承诺声明 ──────────────────────────────────────────────────────────
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
                  children: [new TextRun({ text: '本作品全体参赛队员郑重承诺：', bold: true, font: '仿宋', size: 19 })]
                }),
                new Paragraph({
                  children: [new TextRun({
                    text: '本作品全体参赛队员确认本表所列内容是正式参赛内容的重要组成部分，并严格按照本大类参赛作品类别提交要求提交了评审必需的文档、数据等参赛材料，本表内容按照要求如实填写。如因提交的参赛材料不符合要求，或本表填写内容不属实，将自愿承担因此导致奖项等级降低甚至终止本作品参加比赛的责任。',
                    font: '仿宋', size: 19
                  })]
                }),
                new Paragraph({ children: [], spacing: { before: 120 } }),
                new Paragraph({
                  children: [new TextRun({ text: '全体参赛队员签名：唐浩涵　　李梦琪　　陈思远', font: '仿宋', size: 19 })]
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
  fs.writeFileSync('F:/Desktop/个人资料/学校作业/大三下学期作业/计算机设计大赛/卷积核微课/框架/1-作品信息概要表（已填写）.docx', buf);
  console.log('✅ 作品信息概要表 生成完毕');
}).catch(e => { console.error(e); process.exit(1); });
