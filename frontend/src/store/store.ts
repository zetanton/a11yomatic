import { configureStore } from '@reduxjs/toolkit';
import userReducer from './slices/userSlice';
import pdfReducer from './slices/pdfSlice';

export const store = configureStore({
  reducer: {
    user: userReducer,
    pdfs: pdfReducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        ignoredActions: ['persist/PERSIST'],
      },
    }),
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
