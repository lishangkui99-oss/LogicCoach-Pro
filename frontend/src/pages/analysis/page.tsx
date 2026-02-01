import { useState } from 'react';
import { useNavigate } from 'react-router-dom';

interface Dimension {
  name: string;
  score: number;
}

interface TranscriptItem {
  id: string;
  speaker: 'ai' | 'user';
  text: string;
  highlights: Array<{
    start: number;
    end: number;
    type: 'error' | 'warning';
    feedback: string;
  }>;
}

export default function Analysis() {
  const navigate = useNavigate();
  const [selectedFeedback, setSelectedFeedback] = useState<string | null>(null);
  const [feedbackPosition, setFeedbackPosition] = useState({ x: 0, y: 0 });

  const dimensions: Dimension[] = [
    { name: '业务感', score: 88 },
    { name: '产品力', score: 85 },
    { name: '逻辑思维', score: 82 },
    { name: '沟通能力', score: 78 },
    { name: '项目管理', score: 75 },
    { name: '抗压能力', score: 72 },
    { name: '软技能', score: 68 },
  ];

  const sortedDimensions = [...dimensions].sort((a, b) => b.score - a.score);

  const transcript: TranscriptItem[] = [
    {
      id: '1',
      speaker: 'ai',
      text: '请详细介绍一下你最成功的产品项目。',
      highlights: [],
    },
    {
      id: '2',
      speaker: 'user',
      text: '我做过一个很成功的项目，这个项目很受用户欢迎，我们团队合作得很好，最后取得了不错的成绩。',
      highlights: [
        { start: 0, end: 50, type: 'error', feedback: '太泛泛，缺乏数据支撑和具体细节' },
      ],
    },
    {
      id: '3',
      speaker: 'ai',
      text: '能具体说说你在项目中遇到的最大挑战吗？',
      highlights: [],
    },
    {
      id: '4',
      speaker: 'user',
      text: '最大的挑战是需求变化比较频繁，不过我们通过敏捷开发的方式解决了。我们每周都会开会讨论进度。',
      highlights: [
        { start: 30, end: 50, type: 'warning', feedback: '可以补充具体的敏捷实践方法' },
      ],
    },
    {
      id: '5',
      speaker: 'ai',
      text: '你如何衡量这个产品的成功？',
      highlights: [],
    },
    {
      id: '6',
      speaker: 'user',
      text: '我们的产品上线后，用户增长达到了 300%，日活从 5000 提升到 2 万，用户留存率提升了 45%，NPS 评分达到 72 分。同时，我们将核心功能的转化率从 8% 优化到 23%。',
      highlights: [],
    },
  ];

  const handleHighlightClick = (feedback: string, event: React.MouseEvent) => {
    const rect = (event.target as HTMLElement).getBoundingClientRect();
    setFeedbackPosition({ x: rect.left, y: rect.top - 10 });
    setSelectedFeedback(feedback);
  };

  const handleFeedbackAction = (action: string) => {
    console.log(`Feedback action: ${action}`);
    setSelectedFeedback(null);
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
            <span className="text-7xl font-bold text-white">82</span>
            <span className="text-3xl text-slate-400">/100</span>
          </div>
          <div className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600/20 border border-blue-500/30 rounded-full">
            <i className="ri-medal-line text-blue-400"></i>
            <span className="text-sm font-medium text-blue-300">资深产品经理级别</span>
          </div>
        </div>

        {/* Charts Section */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Radar Chart */}
          <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-6">
            <h3 className="text-lg font-semibold text-white mb-6">7维能力雷达图</h3>
            <div className="relative w-full aspect-square max-w-md mx-auto">
              <svg viewBox="0 0 400 400" className="w-full h-full">
                {/* Background circles */}
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
                
                {/* Axis lines */}
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

                {/* Data polygon */}
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

                {/* Data points */}
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

                {/* Labels */}
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
              {sortedDimensions.map((dimension, index) => (
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

        {/* Transcript & Feedback Section */}
        <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-6">
          <h3 className="text-lg font-semibold text-white mb-6">面试逐字稿 & 反馈</h3>
          <div className="space-y-6">
            {transcript.map((item) => (
              <div key={item.id} className="space-y-2">
                <div className="flex items-center gap-2">
                  <span
                    className={`text-xs font-semibold px-2 py-1 rounded ${
                      item.speaker === 'ai'
                        ? 'bg-slate-700 text-slate-300'
                        : 'bg-blue-600/20 text-blue-300'
                    }`}
                  >
                    {item.speaker === 'ai' ? 'AI 面试官' : '候选人'}
                  </span>
                </div>
                <div className="text-sm text-slate-200 leading-relaxed">
                  {item.highlights.length === 0 ? (
                    <span>{item.text}</span>
                  ) : (
                    <>
                      {item.highlights.map((highlight, idx) => {
                        const before = item.text.slice(
                          idx === 0 ? 0 : item.highlights[idx - 1].end,
                          highlight.start
                        );
                        const highlighted = item.text.slice(highlight.start, highlight.end);
                        const isLast = idx === item.highlights.length - 1;
                        const after = isLast ? item.text.slice(highlight.end) : '';

                        return (
                          <span key={idx}>
                            {before}
                            <span
                              className={`relative px-1 rounded cursor-pointer ${
                                highlight.type === 'error'
                                  ? 'bg-red-500/30 hover:bg-red-500/40'
                                  : 'bg-yellow-500/30 hover:bg-yellow-500/40'
                              }`}
                              onClick={(e) => handleHighlightClick(highlight.feedback, e)}
                            >
                              {highlighted}
                            </span>
                            {after}
                          </span>
                        );
                      })}
                    </>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
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
            <p className="text-sm text-slate-200 mb-3">{selectedFeedback}</p>
            <div className="flex items-center gap-2">
              <button
                onClick={() => handleFeedbackAction('thumbup')}
                className="w-8 h-8 flex items-center justify-center rounded hover:bg-slate-700 transition-colors cursor-pointer"
                title="有帮助"
              >
                <i className="ri-thumb-up-line text-slate-400 hover:text-green-400"></i>
              </button>
              <button
                onClick={() => handleFeedbackAction('thumbdown')}
                className="w-8 h-8 flex items-center justify-center rounded hover:bg-slate-700 transition-colors cursor-pointer"
                title="没帮助"
              >
                <i className="ri-thumb-down-line text-slate-400 hover:text-red-400"></i>
              </button>
              <button
                onClick={() => handleFeedbackAction('edit')}
                className="w-8 h-8 flex items-center justify-center rounded hover:bg-slate-700 transition-colors cursor-pointer"
                title="编辑反馈"
              >
                <i className="ri-edit-line text-slate-400 hover:text-blue-400"></i>
              </button>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
