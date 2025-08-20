# React StrictMode và Double API Calls

## Vấn đề
API được gọi **2 lần** khi load trang trong development mode.

## Nguyên nhân
React.StrictMode (trong file `src/index.tsx`) **cố ý** gọi `useEffect` 2 lần trong development mode để:
- Phát hiện side effects
- Kiểm tra các vấn đề tiềm ẩn
- Đảm bảo component cleanup đúng cách

## Giải pháp đã implement
1. **Sử dụng useRef để prevent duplicate calls**:
   ```tsx
   const hasLoadedRecommendations = useRef(false);
   
   useEffect(() => {
     if (hasLoadedRecommendations.current) {
       console.log('🔄 Already loaded, skipping...');
       return;
     }
     hasLoadedRecommendations.current = true; // Set ngay để prevent race conditions
     // ... API call
   }, []);
   ```

2. **Race condition protection**: Set flag trước khi call API
3. **Error recovery**: Reset flag khi có lỗi để user có thể retry

## Lưu ý quan trọng
- Trong **production mode**: chỉ gọi 1 lần (StrictMode không hoạt động)
- Trong **development mode**: vẫn có thể thấy log 2 lần nhưng API chỉ call 1 lần thực sự
- **KHÔNG nên remove** React.StrictMode vì nó giúp phát hiện bugs

## Kiểm tra
Mở Browser DevTools → Network tab → reload trang → chỉ thấy 1 API call duy nhất
