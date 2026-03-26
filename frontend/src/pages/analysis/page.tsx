import { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';

interface Dimension {
  name: string;
  score: number;
}

interface TranscriptCorrection {
  quote: string;
  type: 'critical' | 'warning';
  reason: string;
}

interface AnalysisData {
  total_score: number;
  level_assessment: string;
  dimensions: Record<string, number>;
  transcript_correction: TranscriptCorrection[];
  improvement_suggestions: string[];
}

interface LocationState {
  transcription?: string;
  ai_analysis?: AnalysisData;
}

const MOCK_ANALYSIS: AnalysisData = {
  total_score: 82,
  level_assessment: '资深产品经理级别',
  dimensions: {
    '业务感': 88, '产品力': 85, '逻辑思维': 82,
    '沟通能力': 78, '项目管理': 75, '抗压能力': 72, '软技能': 68,
  },
  transcript_correction: [
    { quote: '我做过一个很成功的项目，这个项目很受用户欢迎，我们团队合作得很好，最后取得了不错的成绩', type: 'critical', reason: '太泛泛，缺乏数据支撑和具体细节' },
    { quote: '不过我们通过敏捷开发的方式解决了', type: 'warning', reason: '可以补充具体的敏捷实践方法' },
  ],
  improvement_suggestions: [
    '🔥 [致命追问]: 你提到"很成功的项目"，请给出具体的DAU/MAU、转化率等数据指标',
    '💡 [知识库引用]: 建议使用STAR法则重新组织回答结构',
    '✨ [优化建议]: 补充项目背景和你的个人贡献，避免"我们团队"的模糊表述',
  ],
};

const MOCK_TRANSCRIPTION = '请详细介绍一下你最成功的产品项目。我做过一个很成功的项目，这个项目很受用户欢迎，我们团队合作得很好，最后取得了不错的成绩。能具体说说你在项目中遇到的最大挑战吗？最大的挑战是需求变化比较频繁，不过我们通过敏捷开发的方式解决了。我们每周都会开会讨论进度。';

export default function Analysis() {
  const navigate = useNavigate();
  const location = useLocation();
  const state = location.state as LocationState | null;

  const analysis = state?.ai_analysis || MOCK_ANALYSIS;
  const transcription = state?.transcription || MOCK_TRANSCRIPTION;

  const [selectedFeedback, setSelectedFeedback] = useState<string | null>(null);
  const [feedbackPosition, setFeedbackPosition] = useState({ x: 0, y: 0 });

  const dimensionKeys = ['业务感', '产品力', '逻辑思维', '沟通能力', '项目管理', '抗压能力', '软技能'];
  const dimensions: Dimension[] = dimensionKeys.map(name => ({
    name,
    score: analysis.dimensions[name] || 0,
  }));

  const sortedDimensions = [...dimensions].sort((a, b) => b.score - a.score);

  const buildHighlightedHtml = (text: string, corrections: TranscriptCorrection[]) => {
    let html = text;
    corrections.forEach((item) => {
      const colorClass = item.type === 'critical'
        ? 'border-b-2 border-dashed border-red-500 bg-red-500/10 cursor-help'
        : 'border-b-2 border-dashed border-yellow-500 bg-yellow-500/10 cursor-help';
      const escapedReason = item.reason.replace(/"/g, '&quot;');
      html = html.replace(item.quote, `<span class="${colorClass}" title="${escapedReason}">${item.quote}</span>`);
    });
    return html;
  };

  const transcriptHtml = buildHighlightedHtml(transcription, analysis.transcript_correction);

  const handleHighlightClick = (feedback: string, event: React.MouseEvent) => {
    const rect = (event.target as HTMLElement).getBoundingClientRect();
    setFeedbackPosition({ x: rect.left, y: rect.top - 10 });
    setSelectedFeedback(feedback);
  };

  return (
    <div className="min-h-screen bg-slate-900 text-slate-100">
      {/* Header */}
      <header className="border-b border-slate-800 bg-slate-900/80 backdrop-blur-sm">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <img 
              src="https://public.readdy.ai/ai/img_res/9d41dfda-f963-404e-9706-5a9662fdd839.png" 
              alt="LogicCoach Logo" 
              className="h-10 w-10 object-contain"
            />
            <h1 className="text-xl font-semibold text-white">面试分析报告</h1>
          </div>
          <button
            onClick={() => navigate('/')}
            className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-white text-sm font-medium rounded-lg border border-slate-700 transition-colors cursor-pointer whitespace-nowrap"
          >
            返回首页
          </button>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-6 py-12 space-y-12">
        {/* Score Header */}
        <div className="text-center space-y-4">
          <div className="inline-flex items-baseline gap-2">
            <span className="text-7xl font-bold text-white">{analysis.total_score}</span>
            <span className="text-3xl text-slate-400">/100</span>
          </div>
          <div className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600/20 border border-blue-500/30 rounded-full">
            <i className="ri-medal-line text-blue-400"></i>
            <span className="text-sm font-medium text-blue-300">{analysis.level_assessment}</span>
          </div>
        </div>

        {/* Charts Section */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Radar Chart */}
          <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-6">
            <h3 className="text-lg font-semibold text-white mb-6">7维能力雷达图</h3>
            <div className="relative w-full aspect-square max-w-md mx-auto">
              <svg viewBox="0 0 400 400" className="w-full h-full">
                {[0.2, 0.4, 0.6, 0.8, 1].map((scale, i) => (
                  <polygon
                    key={i}
                    points="200,50 331,100 381,231 300,350 100,350 19,231 69,100"
                    fill="none"
                    stroke="#334155"
                    strokeWidth="1"
                    opacity={0.3}
                    transform={`scale(${scale}) translate(${200 - 200 * scale}, ${200 - 200 * scale})`}
                  />
                ))}
                
                {dimensions.map((_, i) => {
                  const angle = (i * 360) / 7 - 90;
                  const x = 200 + 150 * Math.cos((angle * Math.PI) / 180);
                  const y = 200 + 150 * Math.sin((angle * Math.PI) / 180);
                  return (
                    <line
                      key={i}
                      x1="200"
                      y1="200"
                      x2={x}
                      y2={y}
                      stroke="#334155"
                      strokeWidth="1"
                      opacity={0.3}
                    />
                  );
                })}

                <polygon
                  points={dimensions
                    .map((d, i) => {
                      const angle = (i * 360) / 7 - 90;
                      const distance = (d.score / 100) * 150;
                      const x = 200 + distance * Math.cos((angle * Math.PI) / 180);
                      const y = 200 + distance * Math.sin((angle * Math.PI) / 180);
                      return `${x},${y}`;
                    })
                    .join(' ')}
                  fill="#3b82f6"
                  fillOpacity="0.3"
                  stroke="#3b82f6"
                  strokeWidth="2"
                />

                {dimensions.map((d, i) => {
                  const angle = (i * 360) / 7 - 90;
                  const distance = (d.score / 100) * 150;
                  const x = 200 + distance * Math.cos((angle * Math.PI) / 180);
                  const y = 200 + distance * Math.sin((angle * Math.PI) / 180);
                  return (
                    <circle
                      key={i}
                      cx={x}
                      cy={y}
                      r="4"
                      fill="#3b82f6"
                      stroke="#1e40af"
                      strokeWidth="2"
                    />
                  );
                })}

                {dimensions.map((d, i) => {
                  const angle = (i * 360) / 7 - 90;
                  const x = 200 + 180 * Math.cos((angle * Math.PI) / 180);
                  const y = 200 + 180 * Math.sin((angle * Math.PI) / 180);
                  return (
                    <text
                      key={i}
                      x={x}
                      y={y}
                      textAnchor="middle"
                      dominantBaseline="middle"
                      fill="#cbd5e1"
                      fontSize="14"
                      fontWeight="500"
                    >
                      {d.name}
                    </text>
                  );
                })}
              </svg>
            </div>
          </div>

          {/* Bar Chart */}
          <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-6">
            <h3 className="text-lg font-semibold text-white mb-6">能力排序</h3>
            <div className="space-y-4">
              {sortedDimensions.map((dimension) => (
                <div key={dimension.name} className="space-y-2">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-slate-300 font-medium">{dimension.name}</span>
                    <span className="text-blue-400 font-semibold">{dimension.score}</span>
                  </div>
                  <div className="relative h-2 bg-slate-700 rounded-full overflow-hidden">
                    <div
                      className="absolute inset-y-0 left-0 bg-gradient-to-r from-blue-600 to-blue-400 rounded-full transition-all duration-1000"
                      style={{ width: `${dimension.score}%` }}
                    ></div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Transcript with highlights */}
        <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-6">
          <h3 className="text-lg font-semibold text-white mb-6">面试逐字稿 & 反馈</h3>
          <div
            className="text-sm text-slate-200 leading-relaxed"
            dangerouslySetInnerHTML={{ __html: transcriptHtml }}
          />
        </div>

        {/* Improvement Suggestions */}
        {analysis.improvement_suggestions.length > 0 && (
          <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-6">
            <h3 className="text-lg font-semibold text-yellow-500 mb-4">改进建议</h3>
            <ul className="space-y-3 text-sm text-slate-300">
              {analysis.improvement_suggestions.map((s, i) => (
                <li key={i} className="flex gap-2">
                  <span className="text-blue-500 shrink-0">•</span>
                  <span>{s}</span>
                </li>
              ))}
            </ul>
          </div>
        )}
      </main>

      {/* Feedback Tooltip */}
      {selectedFeedback && (
        <>
          <div
            className="fixed inset-0 z-40"
            onClick={() => setSelectedFeedback(null)}
          ></div>
          <div
            className="fixed z-50 bg-slate-800 border border-slate-600 rounded-lg shadow-xl p-4 max-w-xs"
            style={{
              left: `${feedbackPosition.x}px`,
              top: `${feedbackPosition.y}px`,
              transform: 'translate(-50%, -100%)',
            }}
          >
            <p className="text-sm text-slate-200">{selectedFeedback}</p>
          </div>
        </>
      )}
    </div>
  );
}
