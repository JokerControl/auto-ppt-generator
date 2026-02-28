import { useState, useEffect } from 'react';
import axios from 'axios';

interface PPTRecord {
  id: string;
  topic: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  created_at: string;
  download_url?: string;
}

export default function History() {
  const [records, setRecords] = useState<PPTRecord[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchRecords();
  }, []);

  const fetchRecords = async () => {
    try {
      const response = await axios.get('/api/v1/ppt/list');
      const data = response.data;
      if (data.records) {
        setRecords(data.records);
      }
    } catch (error) {
      console.error('Failed to fetch records:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'text-green-500';
      case 'failed':
        return 'text-red-500';
      case 'processing':
        return 'text-yellow-500';
      default:
        return 'text-gray-500';
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-gray-600">加载中...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">生成历史</h1>
        
        {records.length === 0 ? (
          <div className="bg-white rounded-lg shadow p-8 text-center text-gray-500">
            暂无生成记录
          </div>
        ) : (
          <div className="space-y-4">
            {records.map((record) => (
              <div key={record.id} className="bg-white rounded-lg shadow p-6">
                <div className="flex justify-between items-start">
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900">{record.topic}</h3>
                    <p className="text-sm text-gray-500 mt-1">
                      创建时间: {new Date(record.created_at).toLocaleString('zh-CN')}
                    </p>
                  </div>
                  <div className="flex items-center gap-4">
                    <span className={`font-medium ${getStatusColor(record.status)}`}>
                      {record.status === 'completed' && '已完成'}
                      {record.status === 'failed' && '失败'}
                      {record.status === 'processing' && '处理中'}
                      {record.status === 'pending' && '等待中'}
                    </span>
                    {record.download_url && record.status === 'completed' && (
                      <a
                        href={record.download_url}
                        download
                        className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 transition"
                      >
                        下载
                      </a>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
