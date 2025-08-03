import React from 'react';

function TestApp() {
  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-4xl font-bold text-center text-blue-600 mb-8">
          🛒 E-Commerce Test
        </h1>
        <div className="bg-white p-6 rounded-lg shadow-lg">
          <h2 className="text-2xl font-semibold mb-4">Test Component</h2>
          <p className="text-gray-600">
            Nếu bạn thấy trang này, nghĩa là React và TailwindCSS đang hoạt động bình thường.
          </p>
          <div className="mt-4 p-4 bg-blue-100 rounded">
            <p className="text-blue-800">
              ✅ TailwindCSS đang hoạt động
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default TestApp;
