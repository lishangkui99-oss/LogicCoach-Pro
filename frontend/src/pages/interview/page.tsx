import { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

interface Message {
  id: string;
  type: 'ai' | 'user';
  content: string;
  timestamp: Date;
}

export default function Interview() {
  const navigate = useNavigate();
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      type: 'ai',
      content: '你好，我是你的 AI 面试官。今天我们将进行一场产品经理岗位的模拟面试。准备好了吗？',
      timestamp: new Date(),
    },
    {
      id: '2',
      type: 'ai',
      content: '请先做一个简单的自我介绍，包括你的工作经历和主要负责的产品方向。',
      timestamp: new Date(),
    },
  ]);
  const [isRecording, setIsRecording] = useState(false);
  const [recordingTime, setRecordingTime] = useState(0);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const timerRef = useRef<NodeJS.Timeout | null>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    if (isRecording) {
      timerRef.current = setInterval(() => {
        setRecordingTime((prev) => prev + 1);
      }, 1000);
    } else {
      if (timerRef.current) {
        clearInterval(timerRef.current);
      }
      setRecordingTime(0);
    }
    return () => {
      if (timerRef.current) {
        clearInterval(timerRef.current);
      }
    };
  }, [isRecording]);

  const handleRecordingToggle = () => {
    if (!isRecording) {
      setIsRecording(true);
    } else {
      setIsRecording(false);
      // Simulate adding user response
      const newMessage: Message = {
        id: Date.now().toString(),
        type: 'user',
        content: '好的，我来分享一下我的经历。我有 5 年的产品经理经验，主要负责 B 端 SaaS 产品。最近一年，我主导了一个企业协作平台的从 0 到 1 搭建，目前已服务超过 200 家企业客户，月活跃用户达到 5 万人。',
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, newMessage]);

      // Simulate AI response
      setTimeout(() => {
        const aiResponse: Message = {
          id: (Date.now() + 1).toString(),
          type: 'ai',
          content: '很好。请详细介绍一下你最成功的产品项目，包括你在其中的角色、遇到的挑战以及最终的成果。',
          timestamp: new Date(),
        };
        setMessages((prev) => [...prev, aiResponse]);
      }, 1500);
    }
  };

  const handleEndSession = () => {
    navigate('/analysis');
  };

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <div className="min-h-screen bg-slate-900 text-slate-100 flex flex-col">
      {/* Header */}
      <header className="border-b border-slate-800 bg-slate-900/80 backdrop-blur-sm flex-shrink-0">
        <div className="max-w-4xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-2 h-2 rounded-full bg-red-500 animate-pulse"></div>
            <h1 className="text-lg font-semibold text-white">面试进行中</h1>
          </div>
          <button
            onClick={handleEndSession}
            className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white text-sm font-medium rounded-lg transition-colors cursor-pointer whitespace-nowrap"
          >
            结束对话
          </button>
        </div>
      </header>

      {/* Chat Messages */}
      <main className="flex-1 overflow-y-auto">
        <div className="max-w-4xl mx-auto px-6 py-8 space-y-6">
          {messages.map((message) => (
            <div
              key={message.id}
              className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-[75%] rounded-2xl px-5 py-3 ${
                  message.type === 'user'
                    ? 'bg-blue-600 text-white'
                    : 'bg-slate-800 text-slate-100 border border-slate-700'
                }`}
              >
                <p className="text-sm leading-relaxed whitespace-pre-wrap">{message.content}</p>
                <p
                  className={`text-xs mt-2 ${
                    message.type === 'user' ? 'text-blue-200' : 'text-slate-500'
                  }`}
                >
                  {message.timestamp.toLocaleTimeString('zh-CN', {
                    hour: '2-digit',
                    minute: '2-digit',
                  })}
                </p>
              </div>
            </div>
          ))}
          <div ref={messagesEndRef} />
        </div>
      </main>

      {/* Recording Input Area */}
      <div className="border-t border-slate-800 bg-slate-900/80 backdrop-blur-sm flex-shrink-0">
        <div className="max-w-4xl mx-auto px-6 py-8">
          <div className="flex flex-col items-center gap-4">
            {isRecording && (
              <div className="flex items-center gap-3 text-red-400 animate-pulse">
                <div className="w-3 h-3 rounded-full bg-red-500"></div>
                <span className="text-sm font-medium">录音中 {formatTime(recordingTime)}</span>
              </div>
            )}
            
            <button
              onMouseDown={handleRecordingToggle}
              onMouseUp={handleRecordingToggle}
              onTouchStart={handleRecordingToggle}
              onTouchEnd={handleRecordingToggle}
              className={`relative w-32 h-32 rounded-full flex items-center justify-center transition-all cursor-pointer whitespace-nowrap ${
                isRecording
                  ? 'bg-red-600 shadow-lg shadow-red-500/50 scale-110'
                  : 'bg-blue-600 hover:bg-blue-700 hover:shadow-lg hover:shadow-blue-500/30'
              }`}
            >
              <div
                className={`absolute inset-0 rounded-full ${
                  isRecording ? 'animate-ping bg-red-500 opacity-20' : ''
                }`}
              ></div>
              <div className="relative z-10 flex flex-col items-center gap-2">
                <i
                  className={`text-4xl text-white ${
                    isRecording ? 'ri-stop-circle-line' : 'ri-mic-line'
                  }`}
                ></i>
                <span className="text-xs font-medium text-white">
                  {isRecording ? '松开结束' : '按住录音'}
                </span>
              </div>
            </button>

            <p className="text-xs text-slate-400 text-center">
              按住按钮开始录音，松开自动发送
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
