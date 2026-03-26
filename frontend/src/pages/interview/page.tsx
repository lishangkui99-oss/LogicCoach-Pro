import { useState, useRef, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import {
  Chart as ChartJS,
  RadialLinearScale,
  PointElement,
  LineElement,
  Filler,
  Tooltip,
  Legend,
  CategoryScale,
  LinearScale,
  BarElement
} from 'chart.js';
import { Radar, Bar } from 'react-chartjs-2';

// 注册图表组件
ChartJS.register(
  RadialLinearScale, PointElement, LineElement, Filler, Tooltip, Legend,
  CategoryScale, LinearScale, BarElement
);

export default function InterviewCoach() {
  const location = useLocation();
  const navState = location.state as { jdText?: string; resumeFile?: File; mode?: 'mock' | 'upload' } | null;

  // --- 状态管理 ---
  const [isRecording, setIsRecording] = useState(false);
  const [loading, setLoading] = useState(false);
  const [hasResult, setHasResult] = useState(false);
  
  // 输入内容
  const [mode, setMode] = useState<'mock' | 'upload'>(navState?.mode || 'mock');
  const [jdText, setJdText] = useState(navState?.jdText || '');
  const [resumeText, setResumeText] = useState('');
  const [resumeFile, setResumeFile] = useState<File | null>(navState?.resumeFile || null);
  const [question, setQuestion] = useState(''); // 题目展示
  
  // 分析结果数据
  const [score, setScore] = useState(0);
  const [level, setLevel] = useState('');
  const [radarData, setRadarData] = useState<number[]>([0,0,0,0,0,0,0]);
  const [barData, setBarData] = useState<{labels: string[], data: number[]} | null>(null);
  const [transcriptHtml, setTranscriptHtml] = useState('');
  const [suggestions, setSuggestions] = useState<string[]>([]);

  // 录音引用
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);

  // --- 逻辑函数 ---

  // 1. 开始/停止录音
  const toggleRecording = async () => {
    if (!isRecording) {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        const mediaRecorder = new MediaRecorder(stream);
        mediaRecorderRef.current = mediaRecorder;
        audioChunksRef.current = [];

        mediaRecorder.ondataavailable = (e) => {
          if (e.data.size > 0) audioChunksRef.current.push(e.data);
        };

        mediaRecorder.onstop = () => analyzeAudio();
        mediaRecorder.start();
        setIsRecording(true);
      } catch (err) {
        alert("无法访问麦克风，请检查权限");
      }
    } else {
      mediaRecorderRef.current?.stop();
      setIsRecording(false);
    }
  };

  // 2. 发送分析请求
  const analyzeAudio = async () => {
    setLoading(true);
    setHasResult(false);

    const blob = new Blob(audioChunksRef.current, { type: 'audio/wav' });
    const formData = new FormData();
    formData.append("file", blob, "input.wav");
    formData.append("jd_text", jdText || (mode === 'mock' ? "通用面试" : ""));
    formData.append("resume_text", resumeText);
    if (resumeFile) {
      formData.append("resume_file", resumeFile, resumeFile.name);
    }

    try {
      // ⚠️ 注意：这里假设你已经在 vite.config.ts 配置了代理，或者后端开启了 CORS
      // 如果后端在 8000，这里可以直接写完整路径 http://127.0.0.1:8000/analyze_audio
      const res = await fetch("http://127.0.0.1:8000/analyze_audio", { 
        method: "POST", 
        body: formData 
      });
      const data = await res.json();

      if (data.status === "success") {
        processResult(data);
      } else {
        alert("分析失败: " + data.message);
      }
    } catch (error) {
      console.error(error);
      alert("连接服务器失败，请确保后端 uvicorn 已启动");
    } finally {
      setLoading(false);
    }
  };

  // 3. 处理返回结果
  const processResult = (data: any) => {
    const analysis = data.ai_analysis;
    
    // 更新基础信息
    setScore(analysis.total_score);
    setLevel(analysis.level_assessment || "评估中");
    
    // 如果是模拟模式，且用户填了JD，把JD作为题目显示
    if (mode === 'mock' && jdText) {
      setQuestion(jdText);
    }

    // 更新图表数据
    const dims = analysis.dimensions;
    const labels = ['业务感', '产品力', '逻辑思维', '沟通能力', '项目管理', '抗压能力', '软技能'];
    // 确保顺序对应
    const values = [
        dims['业务感'] || 0, dims['产品力'] || 0, dims['逻辑思维'] || 0, 
        dims['沟通能力'] || 0, dims['项目管理'] || 0, dims['抗压能力'] || 0, dims['软技能'] || 0
    ];
    setRadarData(values);

    // 处理排序柱状图
    const sorted = Object.entries(dims).sort(([,a]:any, [,b]:any) => b - a);
    setBarData({
        labels: sorted.map(([k]) => k),
        data: sorted.map(([,v]) => v as number)
    });

    // 处理高亮文本
    let html = data.transcription;
    analysis.transcript_correction.forEach((item: any) => {
      const colorClass = item.type === 'critical' 
        ? 'border-b-2 border-dashed border-red-500 bg-red-500/10 cursor-help' 
        : 'border-b-2 border-dashed border-yellow-500 bg-yellow-500/10 cursor-help';
      // 注意：这里用简单替换，实际生产建议用更严谨的索引匹配
      // 我们把 title 属性作为 Tooltip
      html = html.replace(item.quote, `<span class="${colorClass}" title="${item.reason}">${item.quote}</span>`);
    });
    setTranscriptHtml(html);

    setSuggestions(analysis.improvement_suggestions);
    setHasResult(true);
  };

  // --- UI 渲染 ---
  return (
    <div className="min-h-screen bg-[#0B1121] text-slate-200 font-sans p-6 md:p-10">
      
      {/* 顶部标题 */}
      <header className="max-w-6xl mx-auto mb-8 flex justify-between items-center">
        <div className="flex items-center gap-2">
            <span className="text-blue-500 text-2xl">🤖</span>
            <h1 className="text-xl font-bold">LogicCoach <span className="text-xs bg-blue-900 text-blue-300 px-2 py-0.5 rounded">PRO</span></h1>
        </div>
      </header>

      <div className="max-w-6xl mx-auto space-y-6">
        
        {/* 输入与控制区 */}
        <div className={`bg-[#162032] border border-slate-700 rounded-2xl p-6 transition-all ${loading ? 'opacity-50 pointer-events-none' : ''}`}>
            
            {/* 模式切换 */}
            <div className="flex gap-4 mb-4 text-sm">
                <label className="flex items-center gap-2 cursor-pointer">
                    <input type="radio" checked={mode === 'mock'} onChange={()=>setMode('mock')} className="accent-blue-500"/>
                    模拟面试 (AI出题)
                </label>
                <label className="flex items-center gap-2 cursor-pointer">
                    <input type="radio" checked={mode === 'upload'} onChange={()=>setMode('upload')} className="accent-blue-500"/>
                    录音复盘 (已有录音)
                </label>
            </div>

            <div className="flex gap-4 mb-6 h-32">
                <div className="w-1/2 flex flex-col gap-2">
                    <textarea 
                        className="flex-1 bg-slate-900/50 border border-slate-700 rounded-xl p-3 text-sm focus:border-blue-500 outline-none resize-none"
                        placeholder={mode === 'mock' ? "在此粘贴 JD 或 面试题目..." : "在此粘贴背景信息 (可选)..."}
                        value={jdText}
                        onChange={(e) => setJdText(e.target.value)}
                    />
                    {mode === 'mock' && (
                        <button className="bg-slate-700 hover:bg-slate-600 text-xs py-2 rounded-lg transition text-slate-300">
                            🎲 基于 JD 生成题目 (待实现)
                        </button>
                    )}
                </div>
                <textarea 
                    className="w-1/2 bg-slate-900/50 border border-slate-700 rounded-xl p-3 text-sm focus:border-green-500 outline-none resize-none"
                    placeholder="粘贴你的简历概要..."
                    value={resumeText}
                    onChange={(e) => setResumeText(e.target.value)}
                />
            </div>

            <div className="flex justify-center">
                <button 
                    onClick={toggleRecording}
                    className={`flex items-center gap-2 px-8 py-3 rounded-full text-lg font-bold shadow-lg transition-all ${
                        isRecording 
                        ? 'bg-red-500 hover:bg-red-600 shadow-red-500/20 animate-pulse' 
                        : 'bg-blue-600 hover:bg-blue-500 shadow-blue-500/20'
                    }`}
                >
                    {isRecording ? <><i className="ri-stop-circle-line"></i> 停止并分析</> : <><i className="ri-mic-line"></i> 开始回答</>}
                </button>
            </div>
            <p className="text-center text-slate-500 text-xs mt-3">
                {isRecording ? "正在录音..." : "点击开始录音"}
            </p>
        </div>

        {/* Loading 状态 */}
        {loading && (
            <div className="text-center py-20 animate-fade-in">
                <div className="text-4xl mb-4 animate-spin">⏳</div>
                <p className="text-slate-400">DeepSeek 正在进行深度复盘...</p>
            </div>
        )}

        {/* 结果展示区 */}
        {hasResult && (
            <div className="space-y-6 animate-fade-in-up">
                
                {/* 顶部总分 */}
                <div className="text-center">
                    <div className="inline-flex items-baseline gap-2">
                        <span className="text-6xl font-black text-blue-400">{score}</span>
                        <span className="text-xl text-slate-500">/ 100</span>
                    </div>
                    <div className="mt-2 inline-block bg-blue-900/30 text-blue-300 text-xs px-3 py-1 rounded-full border border-blue-500/30">
                        {level}
                    </div>
                </div>

                {/* 图表区域 */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6 h-[400px]">
                    {/* 雷达图 */}
                    <div className="bg-[#162032] border border-slate-700 rounded-2xl p-4 flex flex-col">
                        <h3 className="text-slate-400 text-sm font-bold mb-4">7维能力雷达</h3>
                        <div className="flex-1 relative">
                            <Radar 
                                data={{
                                    labels: ['业务感', '产品力', '逻辑思维', '沟通能力', '项目管理', '抗压能力', '软技能'],
                                    datasets: [{
                                        label: '得分',
                                        data: radarData,
                                        backgroundColor: 'rgba(59, 130, 246, 0.2)',
                                        borderColor: '#3b82f6',
                                        borderWidth: 2,
                                    }]
                                }}
                                options={{
                                    maintainAspectRatio: false,
                                    scales: {
                                        r: {
                                            angleLines: { color: 'rgba(255,255,255,0.1)' },
                                            grid: { color: 'rgba(255,255,255,0.05)' },
                                            pointLabels: { color: '#94a3b8' },
                                            suggestedMin: 0, suggestedMax: 100,
                                            ticks: { display: false }
                                        }
                                    },
                                    plugins: { legend: { display: false } }
                                }}
                            />
                        </div>
                    </div>

                    {/* 柱状图 */}
                    <div className="bg-[#162032] border border-slate-700 rounded-2xl p-6 flex flex-col">
                        <h3 className="text-slate-400 text-sm font-bold mb-4">能力短板分析</h3>
                        <div className="flex-1 relative">
                            {barData && <Bar 
                                data={{
                                    labels: barData.labels,
                                    datasets: [{
                                        data: barData.data,
                                        backgroundColor: barData.data.map(v => v >= 80 ? '#3b82f6' : v >= 60 ? '#60a5fa' : '#94a3b8'),
                                        borderRadius: 4,
                                        barThickness: 20
                                    }]
                                }}
                                options={{
                                    indexAxis: 'y',
                                    maintainAspectRatio: false,
                                    scales: {
                                        x: { display: false, max: 100 },
                                        y: { 
                                            grid: { display: false },
                                            ticks: { color: '#e2e8f0' }
                                        }
                                    },
                                    plugins: { legend: { display: false } }
                                }}
                            />}
                        </div>
                    </div>
                </div>

                {/* 逐字稿与复盘 */}
                <div className="bg-[#162032] border border-slate-700 rounded-2xl p-8">
                    <h3 className="text-lg font-bold text-white mb-6 border-l-4 border-blue-500 pl-3">面试复盘</h3>
                    
                    <div className="space-y-6">
                        {/* 面试官提问 */}
                        <div className="flex gap-4">
                            <div className="w-10 h-10 rounded-full bg-slate-700 flex items-center justify-center shrink-0">
                                <span className="text-xl">👨‍🏫</span>
                            </div>
                            <div>
                                <p className="text-xs text-slate-500 mb-1">面试官提问</p>
                                <div className="bg-slate-800 text-slate-200 px-5 py-3 rounded-2xl rounded-tl-none border border-slate-700">
                                    {question || "（针对自我介绍或上传内容的通用评估）"}
                                </div>
                            </div>
                        </div>

                        {/* 用户回答 (带高亮) */}
                        <div className="flex gap-4 flex-row-reverse">
                            <div className="w-10 h-10 rounded-full bg-blue-600 flex items-center justify-center shrink-0">
                                <span className="font-bold text-xs text-white">ME</span>
                            </div>
                            <div className="text-right max-w-3xl w-full">
                                <p className="text-xs text-slate-500 mb-1 text-right">你的回答</p>
                                <div 
                                    className="bg-blue-900/20 text-slate-100 px-6 py-4 rounded-2xl rounded-tr-none text-left border border-blue-500/30 leading-relaxed"
                                    dangerouslySetInnerHTML={{ __html: transcriptHtml }}
                                ></div>
                            </div>
                        </div>
                    </div>

                    {/* 建议列表 */}
                    <div className="mt-8 pt-6 border-t border-slate-700/50">
                        <h4 className="text-sm font-bold text-yellow-500 mb-4">💡 改进建议</h4>
                        <ul className="space-y-2 text-sm text-slate-400">
                            {suggestions.map((s, i) => (
                                <li key={i} className="flex gap-2">
                                    <span className="text-blue-500">•</span> {s}
                                </li>
                            ))}
                        </ul>
                    </div>
                </div>
            </div>
        )}

        <div className="h-20"></div>
      </div>
    </div>
  );
}