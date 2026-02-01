import { useState } from 'react';
import { useNavigate } from 'react-router-dom';

export default function Home() {
  const navigate = useNavigate();
  const [resume, setResume] = useState<File | null>(null);
  const [jobDescription, setJobDescription] = useState('');

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setResume(e.target.files[0]);
    }
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setResume(e.dataTransfer.files[0]);
    }
  };

  const startLiveSimulation = () => {
    navigate('/interview');
  };

  const uploadRecording = () => {
    // Handle recording upload
    navigate('/analysis');
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
            <div>
              <h1 className="text-xl font-semibold text-white">LogicCoach</h1>
              <p className="text-xs text-slate-400">AI 产品经理面试教练</p>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-6 py-12">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Left Panel - Context Import */}
          <div className="space-y-6">
            <div>
              <h2 className="text-2xl font-semibold text-white mb-6">上下文导入</h2>
            </div>

            {/* Resume Upload */}
            <div className="space-y-3">
              <label className="text-sm font-medium text-slate-300">上传简历 (PDF)</label>
              <div
                onDragOver={handleDragOver}
                onDrop={handleDrop}
                className="relative border-2 border-dashed border-slate-700 rounded-lg p-8 text-center hover:border-blue-500 transition-colors cursor-pointer bg-slate-800/50"
              >
                <input
                  type="file"
                  accept=".pdf"
                  onChange={handleFileUpload}
                  className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                />
                <div className="flex flex-col items-center gap-3">
                  <div className="w-12 h-12 flex items-center justify-center rounded-full bg-slate-700">
                    <i className="ri-file-upload-line text-2xl text-blue-400"></i>
                  </div>
                  {resume ? (
                    <div className="space-y-1">
                      <p className="text-sm font-medium text-blue-400">{resume.name}</p>
                      <p className="text-xs text-slate-400">点击或拖拽更换文件</p>
                    </div>
                  ) : (
                    <div className="space-y-1">
                      <p className="text-sm font-medium text-slate-300">点击或拖拽上传 PDF</p>
                      <p className="text-xs text-slate-400">支持 PDF 格式，最大 10MB</p>
                    </div>
                  )}
                </div>
              </div>
            </div>

            {/* Job Description */}
            <div className="space-y-3">
              <label className="text-sm font-medium text-slate-300">输入岗位描述 (JD)</label>
              <textarea
                value={jobDescription}
                onChange={(e) => setJobDescription(e.target.value)}
                placeholder="粘贴完整的岗位描述，包括职责、要求等..."
                className="w-full h-64 px-4 py-3 bg-slate-800/50 border border-slate-700 rounded-lg text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
              />
              <p className="text-xs text-slate-400">{jobDescription.length} 字符</p>
            </div>
          </div>

          {/* Right Panel - Action Center */}
          <div className="space-y-6">
            <div>
              <h2 className="text-2xl font-semibold text-white mb-6">操作中心</h2>
            </div>

            {/* Card A - Live Simulation */}
            <button
              onClick={startLiveSimulation}
              className="w-full group relative overflow-hidden rounded-xl bg-gradient-to-br from-blue-600 to-blue-700 p-8 text-left transition-all hover:shadow-lg hover:shadow-blue-500/20 hover:scale-[1.02] cursor-pointer whitespace-nowrap"
            >
              <div className="absolute top-0 right-0 w-32 h-32 bg-blue-400/10 rounded-full -mr-16 -mt-16"></div>
              <div className="relative z-10">
                <div className="w-14 h-14 flex items-center justify-center rounded-xl bg-white/10 mb-4">
                  <i className="ri-mic-line text-3xl text-white"></i>
                </div>
                <h3 className="text-2xl font-semibold text-white mb-2">开始实时模拟</h3>
                <p className="text-blue-100 text-sm">文本提问，语音回答</p>
                <div className="mt-6 flex items-center gap-2 text-white/80 text-sm">
                  <span>立即开始</span>
                  <i className="ri-arrow-right-line group-hover:translate-x-1 transition-transform"></i>
                </div>
              </div>
            </button>

            {/* Card B - Upload Recording */}
            <button
              onClick={uploadRecording}
              className="w-full group relative overflow-hidden rounded-xl bg-slate-800 border border-slate-700 p-8 text-left transition-all hover:border-blue-500 hover:shadow-lg hover:shadow-blue-500/10 hover:scale-[1.02] cursor-pointer whitespace-nowrap"
            >
              <div className="absolute top-0 right-0 w-32 h-32 bg-blue-500/5 rounded-full -mr-16 -mt-16"></div>
              <div className="relative z-10">
                <div className="w-14 h-14 flex items-center justify-center rounded-xl bg-slate-700 mb-4">
                  <i className="ri-upload-cloud-line text-3xl text-blue-400"></i>
                </div>
                <h3 className="text-2xl font-semibold text-white mb-2">上传录音</h3>
                <p className="text-slate-400 text-sm">分析已有面试文件</p>
                <div className="mt-6 flex items-center gap-2 text-slate-400 text-sm group-hover:text-blue-400 transition-colors">
                  <span>选择文件</span>
                  <i className="ri-arrow-right-line group-hover:translate-x-1 transition-transform"></i>
                </div>
              </div>
            </button>

            {/* Info Card */}
            <div className="rounded-lg bg-slate-800/50 border border-slate-700 p-6">
              <div className="flex gap-3">
                <div className="w-10 h-10 flex items-center justify-center rounded-lg bg-blue-500/10 flex-shrink-0">
                  <i className="ri-information-line text-xl text-blue-400"></i>
                </div>
                <div className="space-y-2">
                  <h4 className="text-sm font-medium text-white">使用提示</h4>
                  <ul className="text-xs text-slate-400 space-y-1">
                    <li>• 上传简历和 JD 可获得更精准的评估</li>
                    <li>• 实时模拟支持语音识别和即时反馈</li>
                    <li>• 录音分析支持 MP3、WAV 等常见格式</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
