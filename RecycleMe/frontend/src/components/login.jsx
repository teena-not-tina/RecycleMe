import { useState } from 'react';

export default function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [user, setUser] = useState(null);

  const handleSubmit = async (e) => {
    if (e) e.preventDefault();
    setIsLoading(true);
    setError('');
    
    try {
      const response = await fetch('http://localhost:8000/api/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password }),
      });
      
      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.detail || '로그인에 실패했습니다');
      }
      
      // 토큰을 로컬 스토리지에 저장
      localStorage.setItem('token', data.access_token);
      
      // 사용자 정보 설정
      setUser({
        email,
        username: data.username,
        token: data.access_token
      });
      
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    setUser(null);
  };

  if (user) {
    return (
      <div className="h-screen flex items-center justify-center bg-gray-100">
        <div className="max-w-md w-full p-8 bg-white rounded-lg shadow-lg">
          <h2 className="text-2xl font-bold mb-6 text-center">로그인 성공!</h2>
          <div className="mb-4">
            <p className="text-gray-700">사용자명: <span className="font-semibold">{user.username}</span></p>
            <p className="text-gray-700">이메일: <span className="font-semibold">{user.email}</span></p>
          </div>
          <button
            onClick={handleLogout}
            className="w-full py-2 px-4 bg-red-600 text-white rounded hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500"
          >
            로그아웃
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="h-screen flex items-center justify-center bg-gray-100">
      <div className="max-w-md w-full p-8 bg-white rounded-lg shadow-lg">
        <h2 className="text-2xl font-bold mb-6 text-center">로그인</h2>
        
        {error && (
          <div className="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded">
            {error}
          </div>
        )}
        
        <div>
          <div className="mb-4">
            <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="email">
              이메일
            </label>
            <input
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="이메일 주소를 입력하세요"
            />
          </div>
          
          <div className="mb-6">
            <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="password">
              비밀번호
            </label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="비밀번호를 입력하세요"
            />
          </div>
          
          <div>
            <button
              onClick={handleSubmit}
              disabled={isLoading}
              className="w-full py-2 px-4 bg-blue-600 text-white rounded hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-blue-300"
            >
              {isLoading ? '로그인 중...' : '로그인'}
            </button>
          </div>
        </div>
        
        <div className="mt-4 text-center text-sm">
          <p className="text-gray-600">
            테스트용 계정: user@example.com / password123
          </p>
        </div>
      </div>
    </div>
  );
}